#!/usr/bin/env python3
"""
Extract Google cookies from Chrome on macOS.
Usage: python3 extract_google_cookies.py
"""

import os
import sys
import json
import sqlite3
import shutil
import tempfile
import subprocess
from pathlib import Path

def get_chrome_key():
    """Get Chrome's encryption key from macOS Keychain."""

    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-w',
             '-a', 'Chrome', '-s', 'Chrome Safe Storage'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # Try without -w flag for older macOS
            result = subprocess.run(
                ['security', 'find-generic-password',
                 '-a', 'Chrome', '-s', 'Chrome Safe Storage', '-g'],
                capture_output=True, text=True
            )
            for line in result.stderr.split('\n'):
                if 'password:' in line:
                    return line.split('"')[1].encode()
            return None
        return result.stdout.strip().encode()
    except Exception as e:
        print(f"Warning: Could not get Keychain key: {e}", file=sys.stderr)
        return None

def decrypt_cookie(encrypted_value, key):
    """Decrypt Chrome cookie value on macOS."""
    try:
        from Crypto.Cipher import AES
        import hashlib
        
        # Chrome uses AES-CBC with PBKDF2
        iterations = 1003
        derived_key = hashlib.pbkdf2_hmac(
            'sha1', key, b'saltysalt', iterations, dklen=16
        )
        
        # Remove 'v10' prefix
        encrypted_value = encrypted_value[3:]
        iv = b' ' * 16
        cipher = AES.new(derived_key, AES.MODE_CBC, IV=iv)
        decrypted = cipher.decrypt(encrypted_value)
        
        # Remove PKCS7 padding
        padding = decrypted[-1]
        return decrypted[:-padding].decode('utf-8')
    except ImportError:
        print("Note: pycryptodome not installed, cookies may be unencrypted", file=sys.stderr)
        return None
    except Exception as e:
        return None

def find_chrome_profiles():
    """Find all Chrome profiles."""
    base = Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome'
    if not base.exists():
        print(f"Chrome not found at {base}", file=sys.stderr)
        return []
    
    profiles = []
    for item in base.iterdir():
        cookie_file = item / 'Cookies'
        if cookie_file.exists():
            profiles.append(item)
    return profiles

def extract_cookies(profile_path, domains, key):
    """Extract cookies for given domains from a Chrome profile."""
    cookie_file = profile_path / 'Cookies'
    
    # Copy to temp (Chrome locks the file)
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        shutil.copy2(cookie_file, tmp.name)
        tmp_path = tmp.name
    
    cookies = {}
    try:
        conn = sqlite3.connect(tmp_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        placeholders = ','.join('?' * len(domains))
        cur.execute(f'''
            SELECT host_key, name, value, encrypted_value
            FROM cookies
            WHERE host_key LIKE ? OR host_key LIKE ? OR host_key LIKE ? OR host_key LIKE ?
        ''', ['%google.com', '%.google.com', '%notebooklm%', '%.googleapis.com'])
        
        rows = cur.fetchall()
        for row in rows:
            name = row['name']
            value = row['value']
            
            if not value and row['encrypted_value'] and key:
                value = decrypt_cookie(bytes(row['encrypted_value']), key)
            
            if value:
                cookies[name] = {
                    'value': value,
                    'domain': row['host_key']
                }
        
        conn.close()
    finally:
        os.unlink(tmp_path)
    
    return cookies

def main():
    print("🔍 Looking for Chrome profiles...", file=sys.stderr)
    profiles = find_chrome_profiles()
    
    if not profiles:
        print("❌ No Chrome profiles found", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Found {len(profiles)} profile(s)", file=sys.stderr)
    
    # Get decryption key
    print("🔑 Getting decryption key from Keychain...", file=sys.stderr)
    key = get_chrome_key()
    if key:
        print("✅ Got Keychain key", file=sys.stderr)
    else:
        print("⚠️  No Keychain key, will try unencrypted values only", file=sys.stderr)
    
    domains = ['google.com', 'notebooklm.google.com']
    
    all_cookies = {}
    for profile in profiles:
        print(f"📂 Scanning: {profile.name}", file=sys.stderr)
        try:
            cookies = extract_cookies(profile, domains, key)
            if cookies:
                print(f"  → {len(cookies)} Google cookies found", file=sys.stderr)
                all_cookies.update(cookies)
        except Exception as e:
            print(f"  → Error: {e}", file=sys.stderr)
    
    if not all_cookies:
        print("❌ No cookies found. Make sure you're logged into Google in Chrome.", file=sys.stderr)
        sys.exit(1)
    
    # Output as Netscape cookie format for easy use
    print("\n=== COOKIES (copy everything below) ===")
    for name, info in all_cookies.items():
        print(f"{name}={info['value']}")
    
    print(f"\n✅ Done! Found {len(all_cookies)} cookies", file=sys.stderr)

if __name__ == '__main__':
    main()
