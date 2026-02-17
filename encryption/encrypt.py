"""
encrypt.py - Participant-side encryption script
Usage: python encryption/encrypt.py predictions.csv encryption/public_key.pem submissions/your_team.enc
"""

import sys
import os
import json
import base64
from pathlib import Path

def encrypt_submission(csv_path, public_key_path, output_path):
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        import os as _os
    except ImportError:
        print("❌ Missing dependency. Run: pip install cryptography")
        sys.exit(1)

    # Validate inputs
    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)

    if not Path(public_key_path).exists():
        print(f"❌ Public key not found: {public_key_path}")
        sys.exit(1)

    print(f"🔐 Encrypting: {csv_path}")

    # Read the CSV predictions
    with open(csv_path, 'rb') as f:
        csv_data = f.read()

    # Load public key
    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())

    # Generate a random AES-256 symmetric key for the actual data encryption
    aes_key = _os.urandom(32)
    iv = _os.urandom(16)

    # Encrypt data with AES (fast, handles large files)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(csv_data) + encryptor.finalize()

    # Encrypt the AES key with RSA public key (hybrid encryption)
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Package everything together
    package = {
        'encrypted_key': base64.b64encode(encrypted_aes_key).decode(),
        'iv': base64.b64encode(iv).decode(),
        'encrypted_data': base64.b64encode(encrypted_data).decode(),
        'original_filename': Path(csv_path).name
    }

    # Save encrypted package
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(package, f)

    print(f"✅ Encrypted successfully!")
    print(f"📁 Output: {output_path}")
    print(f"📏 Original size: {len(csv_data)} bytes")
    print(f"📏 Encrypted size: {Path(output_path).stat().st_size} bytes")
    print(f"\n🔒 Your predictions are now encrypted and unreadable without the private key!")
    print(f"\n📤 Next step: Submit {output_path} via Pull Request")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python encryption/encrypt.py <predictions.csv> <public_key.pem> <output.enc>")
        print("Example: python encryption/encrypt.py predictions.csv encryption/public_key.pem submissions/my_team.enc")
        sys.exit(1)

    encrypt_submission(sys.argv[1], sys.argv[2], sys.argv[3])