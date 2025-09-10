import os
import re
import time
import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
import requests


def sanitize_filename(name: str) -> str:
    """
    Replace unsafe characters in a filename with underscores.
    Prevents filesystem issues and promotes safe sharing.
    """
    name = name.strip()
    name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
    return name or "downloaded_image"


def get_filename(url: str, resp: requests.Response) -> str:
    """
    Derive a safe filename based on URL, Content-Disposition, or Content-Type.
    """
    parsed = urlparse(url)
    candidate = os.path.basename(parsed.path)

    if candidate:
        return sanitize_filename(candidate)

    # Try Content-Disposition header
    cd = resp.headers.get("content-disposition", "")
    if "filename=" in cd:
        match = re.search(r'filename="?([^";]+)"?', cd)
        if match:
            return sanitize_filename(match.group(1))

    # Fallback: use Content-Type
    ctype = resp.headers.get("content-type", "").split(";")[0]
    ext = mimetypes.guess_extension(ctype) or ".jpg"
    return f"downloaded_{int(time.time())}{ext}"


def file_hash(path: Path, algo="sha256") -> str:
    """
    Compute a hash of the file content to detect duplicates.
    """
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_image(url: str, dest_dir="Fetched_Images", timeout=10, max_bytes=10_000_000) -> Path | None:
    """
    Download an image from the given URL and save it to dest_dir.
    Returns the path to the saved file, or None if skipped.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are supported.")

    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "UbuntuImageFetcher/2.0 (community tool)"}
    with requests.get(url, stream=True, timeout=timeout, headers=headers) as resp:
        resp.raise_for_status()

        # --- Check HTTP headers carefully ---
        ctype = resp.headers.get("content-type", "")
        if not ctype.startswith("image/"):
            raise ValueError(f"Skipped: not an image (content-type: {ctype})")

        content_length = resp.headers.get("content-length")
        if content_length and int(content_length) > max_bytes:
            raise ValueError(f"Skipped: file too large ({content_length} bytes)")

        last_mod = resp.headers.get("last-modified", "unknown")

        # --- Get safe filename ---
        filename = get_filename(url, resp)
        filepath = Path(dest_dir) / filename

        # Avoid overwriting by appending timestamp if exists
        if filepath.exists():
            filepath = filepath.with_stem(filepath.stem + f"_{int(time.time())}")

        # --- Stream download ---
        total = 0
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    f.close()
                    filepath.unlink(missing_ok=True)
                    raise ValueError("File exceeds maximum allowed size.")
                f.write(chunk)

    # --- Duplicate check via hashing ---
    file_digest = file_hash(filepath)
    for existing in Path(dest_dir).glob("*"):
        if existing == filepath:
            continue
        if file_hash(existing) == file_digest:
            filepath.unlink(missing_ok=True)
            print(f"⚠ Skipped duplicate of {existing.name}")
            return None

    print(f"✓ Saved {filepath.name} ({total} bytes, last modified: {last_mod})")
    return filepath


def main():
    print("🌍 Ubuntu Image Fetcher")
    print("Mindful multi-image downloader for safe and respectful use.\n")

    urls = input("Enter image URLs (separated by spaces): ").split()

    for url in urls:
        try:
            download_image(url)
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error for {url}: {e}")
        except ValueError as e:
            print(f"✗ Skipped {url}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error for {url}: {e}")

    print("\n🤝 All tasks complete. Community strengthened, knowledge shared.")


if __name__ == "__main__":
    main()
