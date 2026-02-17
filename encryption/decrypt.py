"""
decrypt.py - Server-side decryption script (runs in GitHub Actions)
Usage: python encryption/decrypt.py submissions/team.enc encryption/private_key.pem decrypted_predictions.csv
NEVER share or expose the private key!
"""

import sys
import os
import json
import base64
from pathlib import Path


def decrypt_submission(enc_path, private_key_path, output_path):
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        print("❌ Missing dependency. Run: pip install cryptography")
        sys.exit(1)

    # Validate inputs
    if not Path(enc_path).exists():
        print(f"❌ Encrypted file not found: {enc_path}")
        sys.exit(1)

    if not Path(private_key_path).exists():
        print(f"❌ Private key not found: {private_key_path}")
        sys.exit(1)

    print(f"🔓 Decrypting: {enc_path}")

    # Load encrypted package
    with open(enc_path, 'r') as f:
        package = json.load(f)

    # Load private key
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Decrypt the AES key using RSA private key
    encrypted_aes_key = base64.b64decode(package['encrypted_key'])
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the actual data using AES
    iv = base64.b64decode(package['iv'])
    encrypted_data = base64.b64decode(package['encrypted_data'])

    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    csv_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Save decrypted CSV
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(csv_data)

    print(f"✅ Decrypted successfully!")
    print(f"📁 Output: {output_path}")

    return output_path


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python encryption/decrypt.py <encrypted.enc> <private_key.pem> <output.csv>")
        sys.exit(1)

    decrypt_submission(sys.argv[1], sys.argv[2], sys.argv[3])