#!/usr/bin/env python3
"""
Decrypt Chrome cookies from macOS without Keychain access.
Requires the Chrome Safe Storage key exported from Mac Keychain.

Usage:
  python3 decrypt_chrome_cookies.py --domain .claude.ai --name sessionKey
"""

import argparse
import hashlib
import sqlite3
import struct
import sys
from pathlib import Path

# pip install cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

COOKIE_DB = Path("/home/node/chrome-profile/Cookies")
KEY_FILE = Path("/home/node/.openclaw/secrets/chrome-safe-storage-key.txt")


def derive_key(safe_storage_key: str) -> bytes:
    """Derive AES key from Chrome Safe Storage password (macOS method)."""
    # macOS Chrome uses PBKDF2 with the safe storage key
    return hashlib.pbkdf2_hmac(
        "sha1",
        safe_storage_key.encode("utf-8"),
        b"saltysalt",
        1003,
        dklen=16,
    )


def decrypt_cookie_value(encrypted_value: bytes, key: bytes) -> str:
    """Decrypt a Chrome cookie value (v10 format on macOS)."""
    if encrypted_value[:3] == b"v10":
        encrypted_value = encrypted_value[3:]
        iv = b" " * 16  # 16 spaces
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_value) + decryptor.finalize()
        # Remove PKCS7 padding
        padding_len = decrypted[-1]
        if isinstance(padding_len, int) and 1 <= padding_len <= 16:
            decrypted = decrypted[:-padding_len]
        return decrypted.decode("utf-8", errors="replace")
    else:
        # Not encrypted or unknown format
        return encrypted_value.decode("utf-8", errors="replace")


def get_cookies(domain: str, name: str = None) -> list[dict]:
    """Get decrypted cookies for a domain."""
    safe_storage_key = KEY_FILE.read_text().strip()
    key = derive_key(safe_storage_key)

    # Copy DB to avoid lock issues
    import shutil, tempfile
    tmp = Path(tempfile.mktemp(suffix=".db"))
    shutil.copy2(COOKIE_DB, tmp)

    db = sqlite3.connect(str(tmp))
    cursor = db.cursor()

    query = "SELECT name, encrypted_value, host_key, path, expires_utc FROM cookies WHERE host_key LIKE ?"
    params = [f"%{domain}%"]
    if name:
        query += " AND name = ?"
        params.append(name)

    cursor.execute(query, params)
    results = []
    for row in cursor.fetchall():
        cookie_name, enc_value, host, path, expires = row
        value = decrypt_cookie_value(enc_value, key)
        results.append({
            "name": cookie_name,
            "value": value,
            "host": host,
            "path": path,
        })

    db.close()
    tmp.unlink()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default=".claude.ai")
    parser.add_argument("--name", default=None, help="Cookie name filter")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cookies = get_cookies(args.domain, args.name)

    if args.json:
        import json
        print(json.dumps(cookies, indent=2))
    else:
        for c in cookies:
            print(f"{c['name']}={c['value']}")


if __name__ == "__main__":
    main()
