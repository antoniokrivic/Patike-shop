"""
Management command: čita slike iz Firebase Storage i mapira ih na proizvode u bazi.
Za svaki proizvod bira najnoviju uploadanu sliku (po blob.time_created).
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime

from django.core.management.base import BaseCommand

import firebase_admin
from firebase_admin import storage


# ──────────────────────────────────────────────────────────────
# Ključne riječi za mapiranje Firebase naziva → Product(id)
# Format: product_id → lista stringova koje tražimo u nazivu blob-a (case‑insensitive)
# ──────────────────────────────────────────────────────────────
PRODUCT_KEYWORDS: dict[int, list[str]] = {
    # ── Nike ───────────────────────────────────────────────
    1:  ["air-max", "airmax", "air_max"],                         # Air Max 90
    2:  ["air-force", "airforce", "air_force", "DH8010"],         # Air Force 1
    3:  ["vapormax", "vapor-max"],                                # Air VaporMax
    4:  ["react-infinity", "react_infinity"],                     # React Infinity Run
    5:  ["invincible", "zoomx", "IO9974"],                        # ZoomX Invincible
    6:  ["pegasus-trail", "pegasus_trail"],                       # Pegasus Trail
    7:  ["blazer"],                                               # Blazer Mid
    8:  ["dunk", "sb-dunk", "sb_dunk"],                           # SB Dunk Low
    9:  ["pegasus-41", "zoom-pegasus", "air-zoom-pegasus",
         "pegasus-running", "pegasus-4"],                         # Air Zoom Pegasus
    10: ["cortez"],                                               # Cortez

    # ── Adidas ─────────────────────────────────────────────
    11: ["ultraboost", "ultra-boost", "ultra_boost", "FY7757"],   # Ultraboost 1.0 DNA
    12: ["nmd", "FV1689"],                                        # NMD_R1
    13: ["superstar", "IG3321"],                                  # Superstar
    14: ["stan-smith", "stan_smith", "stansmith", "FX5502"],       # Stan Smith
    15: ["forum", "FV3284"],                                      # Forum Low
    16: ["gazelle", "JI2060"],                                    # Gazelle
    17: ["campus"],                                               # Campus 00s
    18: ["adizero", "boston-12", "boston12"],                      # Adizero Boston 12
    19: ["samba", "EE5450"],                                      # Samba OG
    20: ["solarglide", "solar-glide", "solar_glide"],             # Solar Glide 6

    # ── New Balance ────────────────────────────────────────
    21: ["990v6", "990nc6", "u990"],                              # 990v6
    22: ["bb550", "550ha"],                                       # 550
    23: ["ph327", "gs327", "ws327"],                              # 327
    24: ["1080v13"],                                              # Fresh Foam 1080v13
    25: ["fuelcell", "fuel-cell", "fuel_cell"],                   # FuelCell Rebel v3
    26: ["u998gr", "u998", "made-in-usa-998"],                    # Made in USA 998
    27: ["xc-72", "xc72", "uxc72"],                               # XC-72
    28: ["more-v4", "morag", "more_v4", "fresh-foam-x-more"],    # Fresh Foam X More v4
    29: ["574"],                                                  # 574 Core
    30: ["860v13"],                                               # 860v13

    # ── Vans ───────────────────────────────────────────────
    31: ["old-skool", "old_skool", "oldskool",
         "VN000EWZ"],                                             # Old Skool
    32: ["sk8-hi", "sk8_hi", "sk8hi"],                            # Sk8-Hi
    33: ["authentic"],                                            # Authentic
    34: ["\\bera\\b"],                                            # Era (word boundary)
    35: ["slip-on", "slip_on", "slipon",
         "classic-slip"],                                         # Slip-On
    36: ["ultrarange", "ultra-range"],                             # UltraRange Exo
    37: ["rowan"],                                                # Rowan 2
    38: ["ave-pro", "ave_pro", "avepro"],                         # AVE Pro
    39: ["kyle"],                                                 # Kyle Pro 2
    40: ["half-cab", "half_cab", "halfcab"],                      # Half Cab
}


# Dodatno: poznati Adidas/Nike article kodovi → product id
# (kad naziv fajla sadrži samo kod, a ne ime modela)
ARTICLE_CODE_MAP: dict[str, int] = {
    "VA3TKN6BT": 32,  # Vans Sk8-Hi
}


def _strip_uuid_prefix(blob_name: str) -> str:
    """Iz 'products/abc123def_filename.jpg' izvlači 'filename.jpg'."""
    basename = blob_name.split("/")[-1]
    # UUID hex je 32 znaka, pa format je: 32hex_rest
    match = re.match(r"[0-9a-f]{32}_(.+)", basename, re.IGNORECASE)
    return match.group(1) if match else basename


def _match_blob_to_product(blob_name: str) -> int | None:
    """Pokušava mapirati blob na product ID koristeći ključne riječi i article kodove."""
    # Koristi samo ime fajla (bez UUID prefiksa) za matching
    filename = _strip_uuid_prefix(blob_name)
    filename_lower = filename.lower()

    # 1) Probaj article kodove (npr. VA3TKN6BT)
    for code, pid in ARTICLE_CODE_MAP.items():
        if code.lower() in filename_lower:
            return pid

    # 2) Probaj ključne riječi (podržava regex pattern s \b za word boundary)
    for pid, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if kw.startswith("\\b") or "\\b" in kw:
                # Regex pattern - koristi re.search
                if re.search(kw, filename_lower, re.IGNORECASE):
                    return pid
            elif kw.lower() in filename_lower:
                return pid

    return None


class Command(BaseCommand):
    help = "Mapira slike iz Firebase Storage na proizvode i ažurira image_url."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Samo prikaži mapiranje, ne mijenjaj bazu.",
        )

    def handle(self, *args, **options):
        from shop.firebase_storage import load_firebase_storage_config, _get_or_init_app
        from shop.models import Product

        dry_run = options["dry_run"]

        cfg = load_firebase_storage_config()
        _get_or_init_app(cfg)

        bucket = storage.bucket(name=cfg.bucket_name)
        blobs = list(bucket.list_blobs(prefix="products/"))

        self.stdout.write(f"Pronađeno {len(blobs)} blob-ova u Firebase Storage.\n")

        # Grupiraj blobove po product ID-u
        product_blobs: dict[int, list] = defaultdict(list)
        unmatched = []

        for blob in blobs:
            pid = _match_blob_to_product(blob.name)
            if pid:
                product_blobs[pid].append(blob)
            else:
                unmatched.append(blob.name)

        # Za svaki proizvod, uzmi najnoviji blob
        updated = 0
        for pid in sorted(product_blobs.keys()):
            candidates = product_blobs[pid]
            # Sortiraj po vremenu kreiranja (najnoviji prvi)
            candidates.sort(
                key=lambda b: b.time_created or datetime.min.replace(tzinfo=None),
                reverse=True,
            )
            best = candidates[0]
            # Napravi public URL
            best.make_public()
            url = best.public_url

            try:
                product = Product.objects.get(id=pid)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  [SKIP] Product ID={pid} ne postoji u bazi."
                ))
                continue

            old_url = product.image_url or "(prazno)"
            filename = _strip_uuid_prefix(best.name)

            if dry_run:
                self.stdout.write(
                    f"  [DRY] ID={pid:>2} {product.brand} - {product.title}\n"
                    f"        file: {filename}\n"
                    f"        old:  {old_url[:80]}\n"
                    f"        new:  {url[:80]}\n"
                )
            else:
                product.image_url = url
                product.image = None  # Firebase URL, ne lokalni fajl
                product.save(update_fields=["image_url", "image"])
                updated += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  [OK] ID={pid:>2} {product.brand} - {product.title} ← {filename}"
                ))

        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"\n⚠ {len(unmatched)} blob(ova) nije mapirano na proizvod:"
            ))
            for name in unmatched:
                self.stdout.write(f"  - {name}")

        # Provjeri proizvode koji nemaju Firebase sliku
        all_pids = set(Product.objects.values_list("id", flat=True))
        matched_pids = set(product_blobs.keys())
        missing = all_pids - matched_pids
        if missing:
            self.stdout.write(self.style.WARNING(
                f"\n⚠ {len(missing)} proizvod(a) bez Firebase slike:"
            ))
            for pid in sorted(missing):
                try:
                    p = Product.objects.get(id=pid)
                    self.stdout.write(f"  - ID={pid} {p.brand} - {p.title}")
                except Product.DoesNotExist:
                    pass

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nAžurirano {updated} proizvod(a)."
            ))
