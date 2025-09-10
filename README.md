# Ubuntu_Requests

week 6 python assignment

Ubuntu Image Fetcher

A mindful, safe, and community-oriented multi-image downloader that respects the web while helping you fetch images easily.

This script is written in Python and ensures security, duplicate prevention, and responsible downloading practices.

✨ Features

✅ Download multiple images at once from given URLs.

✅ Safe filename handling — replaces unsafe characters.

✅ Checks HTTP headers:

Ensures file is an image (Content-Type).

Respects Content-Length to avoid oversized downloads.

✅ Duplicate prevention using SHA-256 hashing.

✅ Streaming download to handle large files efficiently.

✅ Custom User-Agent for respectful web scraping.

✅ Cross-platform compatibility (Linux, Windows, macOS).

📦 Requirements

Python 3.10+

Dependencies:

requests

Install requirements with:

pip install requests
