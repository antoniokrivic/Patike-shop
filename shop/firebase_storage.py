from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Optional

import firebase_admin
from firebase_admin import credentials, storage

# Korijenski direktorij projekta (dva nivoa iznad shop/)
BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class FirebaseStorageConfig:
    # Konfiguracija se čita iz env varijabli:
    # - FIREBASE_SERVICE_ACCOUNT_PATH: putanja do service account JSON-a
    # - FIREBASE_STORAGE_BUCKET: naziv bucket-a
    # - FIREBASE_STORAGE_PUBLIC: 1=public URL, 0=signed URL

    service_account_path: str
    bucket_name: str
    make_public: bool = True


_app: Optional[firebase_admin.App] = None


def load_firebase_storage_config() -> FirebaseStorageConfig:
    raw_path = (os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH") or "").strip()
    bucket_name = (os.environ.get("FIREBASE_STORAGE_BUCKET") or "").strip()
    make_public = (os.environ.get("FIREBASE_STORAGE_PUBLIC", "1").strip() == "1")

    # Ako je putanja relativna, razriješi je u odnosu na korijen projekta
    if raw_path and not os.path.isabs(raw_path):
        service_account_path = str(BASE_DIR / raw_path)
    else:
        service_account_path = raw_path

    if not service_account_path:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_PATH is not set. "
            "Set it to the path of your Firebase service account JSON."
        )

    if not bucket_name:
        raise RuntimeError(
            "FIREBASE_STORAGE_BUCKET is not set. "
            'Example: "your-project-id.appspot.com" or "your-project-id.firebasestorage.app".'
        )

    return FirebaseStorageConfig(
        service_account_path=service_account_path,
        bucket_name=bucket_name,
        make_public=make_public,
    )


def _get_or_init_app(cfg: FirebaseStorageConfig) -> firebase_admin.App:
    global _app
    if _app is not None:
        return _app

    cred = credentials.Certificate(cfg.service_account_path)
    _app = firebase_admin.initialize_app(
        cred,
        {
            # Koristi firebase_admin.storage.bucket() kad naziv bucket-a nije eksplicitno proslijeđen.
            "storageBucket": cfg.bucket_name,
        },
    )
    return _app


def upload_fileobj_to_firebase(
    *,
    fileobj: BinaryIO,
    destination_path: str,
    content_type: Optional[str] = None,
) -> str:
    # Upload-a file objekt na Firebase Storage i vraća URL.
    # Ako je FIREBASE_STORAGE_PUBLIC=1, vraća se public URL (potrebna pravila/permissioni).
    # Ako je FIREBASE_STORAGE_PUBLIC=0, vraća se signed URL (vrijedi 1h).

    cfg = load_firebase_storage_config()
    _get_or_init_app(cfg)

    bucket = storage.bucket(name=cfg.bucket_name)
    blob = bucket.blob(destination_path)

    blob.upload_from_file(fileobj, content_type=content_type)

    if cfg.make_public:
        blob.make_public()
        return blob.public_url

    return blob.generate_signed_url(expiration=3600)
