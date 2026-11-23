from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache
def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def upload_file(path: str, data: bytes, content_type: str = "application/pdf") -> None:
    get_supabase().storage.from_(settings.storage_bucket).upload(
        path, data, {"content-type": content_type, "upsert": "true"}
    )


def download_file(path: str) -> bytes:
    return get_supabase().storage.from_(settings.storage_bucket).download(path)


def remove_files(paths: list[str]) -> None:
    if paths:
        get_supabase().storage.from_(settings.storage_bucket).remove(paths)
