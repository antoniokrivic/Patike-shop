from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from django.core.management.base import BaseCommand

from shop.models import Product


@dataclass(frozen=True)
class ModelProfile:
	# Profil modela koji pomaže generirati opis (konzistentno, ali dovoljno različito po modelima).
	category: str  # lifestyle | running | skate | classic


def _profile_for(title: str) -> ModelProfile:
	name = (title or "").lower()

	if any(k in name for k in [
		"trail",
		"run",
		"runner",
		"rebel",
		"1080",
		"glide",
		"boston",
		"adizero",
		"pegasus",
		"invincible",
		"infinity",
		"zoomx",
		"vapormax",
		]):
		return ModelProfile(category="running")

	if any(k in name for k in [
		"sk8",
		"old skool",
		"authentic",
		"era",
		"slip",
		"half cab",
		"rowan",
		"kyle",
		"ave",
		]):
		return ModelProfile(category="skate")

	if any(k in name for k in [
		"stan smith",
		"superstar",
		"gazelle",
		"samba",
		"campus",
		"forum",
		"cortez",
		"blazer",
		]):
		return ModelProfile(category="classic")

	return ModelProfile(category="lifestyle")


def _deterministic_index(seed: str, n: int) -> int:
	# Deterministički indeks u rasponu [0, n) - isti seed uvijek daje isti rezultat.
	if n <= 0:
		return 0
	h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
	return int(h[:8], 16) % n


def _pick(seed: str, options: list[str]) -> str:
	return options[_deterministic_index(seed, len(options))]


def _cleanup(text: str) -> str:
	# Normalize whitespace, avoid double spaces.
	text = re.sub(r"\s+", " ", text).strip()
	return text


def _build_description(title: str) -> str:
	# Generira opis proizvoda (3 rečenice) na hrvatskom, na temelju naziva modela.
	profile = _profile_for(title)
	seed = (title or "").strip()

	openers = [
		"spajaju prepoznatljivu siluetu i moderan detalj",
		"donose čist, nosiv dizajn za svaki dan",
		"ističu se jednostavnim linijama i dobrim balansom stila i funkcionalnosti",
		"dolaze s profinjenim izgledom koji lako uklopiš u outfit",
		"daju svjež twist klasičnom streetwearu",
	]

	materials = [
		"Gornjište je ugodno i dovoljno prozračno za cjelodnevno nošenje",
		"Materijali na gornjištu daju dobar osjećaj na stopalu i uredan izgled",
		"Kombinacija panela i šavova daje strukturu bez osjećaja krutosti",
		"Detalji na gornjištu dodaju karakter, ali zadržavaju čist izgled",
		"Završna obrada je minimalistička i lako se kombinira",
	]

	outsoles = [
		"Potplat drži stabilno i pruža dobar kontakt s podlogom",
		"Stabilan potplat daje sigurnost u hodu i u gužvi grada",
		"Profil potplata pomaže u prianjanju i svakodnevnoj izdržljivosti",
		"Osjećaj pod stopalom je mekan, ali kontroliran za cijeli dan",
		"Uložen trud u udobnost se osjeti već nakon prvog koraka",
	]

	styling = [
		"Najbolje izgledaju uz traperice, cargo hlače ili trenirku",
		"Odlično sjedaju uz jednostavan hoodie i oversized majicu",
		"Isprobaj ih uz neutralne tonove za clean look",
		"Za više kontrasta kombiniraj ih s tamnim outfitom",
		"Super su izbor kad želiš jednu patiku za više kombinacija",
	]

	use_cases_running = [
		"za lagano trčanje, šetnje i aktivne dane",
		"kad želiš udobnost na većoj kilometraži i u hodu",
		"za trening, putovanja i sve kad si stalno u pokretu",
		"za duže šetnje po gradu i vikend aktivnosti",
		"za tempo dana kad ti je bitna mekoća i stabilnost",
	]
	use_cases_skate = [
		"za skate vibru, grad i ležerne izlaske",
		"za svakodnevno nošenje kad želiš čvršći osjećaj i dobar grip",
		"za street stil i dane kad si stalno vani",
		"za opuštene kombinacije i urbanu vožnju",
		"za casual outfite s malo karaktera",
	]
	use_cases_classic = [
		"za minimalističke kombinacije i uredan streetwear",
		"za smart-casual look bez puno razmišljanja",
		"kad želiš klasičan par koji ne izlazi iz mode",
		"za posao, školu i vikend izlazak",
		"za svakodnevni look s dozom retro šarma",
	]
	use_cases_lifestyle = [
		"za svaki dan, posao ili školu",
		"za gradski tempo i brze kombinacije",
		"za svakodnevne outfite i putovanja",
		"za casual look koji izgleda sređeno",
		"kad želiš udobnu patiku koja ide uz sve",
	]

	# Category-specific wording to reduce repetition.
	if profile.category == "running":
		use_case = _pick(seed + "|use", use_cases_running)
		mid = _pick(seed + "|mid", [
			"Mekši osjećaj pri koraku pomaže kad si dugo na nogama",
			"Udobnost je u prvom planu, bez da patika izgleda previše sportski",
			"Dizajn je sportski, ali dovoljno clean za svakodnevni outfit",
			"Kroj je siguran, a osjećaj pod stopalom ostaje stabilan",
			"Lako ih nosiš od treninga do grada bez promjene tenisica",
		])
	elif profile.category == "skate":
		use_case = _pick(seed + "|use", use_cases_skate)
		mid = _pick(seed + "|mid", [
			"Čvršći osjećaj i stabilnost daju samopouzdanje na dasci i u hodu",
			"Street karakter je odmah prepoznatljiv, ali ostaje nosiv",
			"Konstrukcija djeluje robusno, ali i dalje udobno",
			"Dobro sjede na stopalu i drže formu kroz dan",
			"Ako voliš skate estetiku, ovo je siguran pogodak",
		])
	elif profile.category == "classic":
		use_case = _pick(seed + "|use", use_cases_classic)
		mid = _pick(seed + "|mid", [
			"Retro dojam je tu, ali linije su dovoljno moderne",
			"To je onaj par koji možeš nositi cijelu sezonu",
			"Jednostavnost im je najveća prednost — uklapaju se svugdje",
			"Dobiješ klasičan look bez žrtvovanja udobnosti",
			"Kad želiš clean tenisicu, teško je pogriješiti",
		])
	else:
		use_case = _pick(seed + "|use", use_cases_lifestyle)
		mid = _pick(seed + "|mid", [
			"Dovoljno su upečatljive da podignu outfit, ali nikad napadne",
			"Praktične su i nosive, idealne za tvoj daily rotation",
			"Balansiraju udobnost i stil bez previše detalja",
			"Odlično rade i s ležernim i s malo sređenijim kombinacijama",
			"Ako tražiš jedan par za većinu situacija, ovo je to",
		])

	s1 = f"{title} {_pick(seed + '|open', openers)}."
	s2 = f"{_pick(seed + '|mat', materials)}; {mid.lower()}."
	s3 = f"{_pick(seed + '|out', outsoles)} — {use_case}, i {_pick(seed + '|sty', styling).lower()}."

	return _cleanup(f"{s1} {s2} {s3}")


class Command(BaseCommand):
	help = (
		"Populate Product.description with short Croatian descriptions (2–3 sentences). "
		"By default only fills empty descriptions."
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--overwrite",
			action="store_true",
			help="Overwrite existing descriptions (default: only fill empty).",
		)

	def handle(self, *args, **options):
		overwrite: bool = bool(options.get("overwrite"))

		qs = Product.objects.all().order_by("id")
		updated = 0

		for product in qs:
			if (product.description or "").strip() and not overwrite:
				continue

			product.description = _build_description(product.title or "Ove patike")
			product.save(update_fields=["description"])
			updated += 1

		self.stdout.write(self.style.SUCCESS(f"Updated {updated} products."))
