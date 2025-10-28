"""
PGP Service for handling encryption, decryption, and key management
"""
import os
import gnupg
import tempfile
from typing import Optional, List, Dict, Any, Tuple
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class PGPService:
    """Service class for PGP operations using python-gnupg."""

    def __init__(self, gnupg_home: Optional[str] = None):
        """Initialize the PGP service with a GnuPG home directory."""
        logger.info("Initializing PGP service")

        if gnupg_home is None:
            gnupg_home = current_app.config.get('GNUPG_HOME')

        self.gnupg_home = gnupg_home
        logger.info(f"Using GnuPG home directory: {self.gnupg_home}")

        os.makedirs(self.gnupg_home, exist_ok=True)

        # Initialize GnuPG
        self.gpg = gnupg.GPG(gnupghome=self.gnupg_home)
        logger.info("PGP service initialized successfully")

    def generate_key_pair(self, name: str, email: str, passphrase: str = None,
                          key_type: str = "RSA", key_length: int = 2048) -> Dict[str, Any]:
        """
        Generate a new PGP key pair.

        Args:
            name: Full name for the key
            email: Email address for the key
            passphrase: Optional passphrase to protect the private key
            key_type: Type of key (RSA, DSA, etc.)
            key_length: Length of the key in bits

        Returns:
            Dictionary with key generation results
        """
        try:
            input_data = self.gpg.gen_key_input(
                name_real=name,
                name_email=email,
                passphrase=passphrase,
                key_type=key_type,
                key_length=key_length
            )

            key = self.gpg.gen_key(input_data)

            if key.fingerprint:
                return {
                    'success': True,
                    'fingerprint': key.fingerprint,
                    'message': f'Key pair generated successfully for {name} <{email}>'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to generate key pair'
                }

        except Exception as e:
            logger.error(f"Error generating key pair: {str(e)}")
            return {
                'success': False,
                'message': f'Error generating key pair: {str(e)}'
            }

    def list_keys(self, secret: bool = False) -> List[Dict[str, Any]]:
        """
        List all public or private keys.

        Args:
            secret: If True, list private keys; if False, list public keys

        Returns:
            List of key dictionaries
        """
        try:
            keys = self.gpg.list_keys(secret=secret)
            formatted_keys = []

            for key in keys:
                formatted_key = {
                    'fingerprint': key['fingerprint'],
                    'keyid': key['keyid'],
                    'type': key['type'],
                    'length': key['length'],
                    'algo': key['algo'],
                    'date': key['date'],
                    'expires': key['expires'],
                    'uids': key['uids'],
                    'trust': key.get('trust', 'unknown')
                }
                formatted_keys.append(formatted_key)

            return formatted_keys

        except Exception as e:
            logger.error(f"Error listing keys: {str(e)}")
            return []

    def import_key(self, key_data: str) -> Dict[str, Any]:
        """
        Import a PGP key from key data.

        Args:
            key_data: The key data as a string

        Returns:
            Dictionary with import results
        """
        try:
            import_result = self.gpg.import_keys(key_data)

            if import_result.count > 0:
                return {
                    'success': True,
                    'count': import_result.count,
                    'fingerprints': import_result.fingerprints,
                    'message': f'Successfully imported {import_result.count} key(s)'
                }
            else:
                return {
                    'success': False,
                    'message': 'No keys were imported'
                }

        except Exception as e:
            logger.error(f"Error importing key: {str(e)}")
            return {
                'success': False,
                'message': f'Error importing key: {str(e)}'
            }

    def export_key(self, keyid: str, secret: bool = False) -> Optional[str]:
        """
        Export a key by its ID.

        Args:
            keyid: The key ID or fingerprint
            secret: If True, export private key; if False, export public key

        Returns:
            Key data as string or None if error
        """
        try:
            return self.gpg.export_keys(keyid, secret=secret)
        except Exception as e:
            logger.error(f"Error exporting key {keyid}: {str(e)}")
            return None

    def encrypt_data(self, data: bytes, recipient_keyids: List[str],
                     armor: bool = True) -> Dict[str, Any]:
        """
        Encrypt data for specified recipients.

        Args:
            data: Data to encrypt
            recipient_keyids: List of recipient key IDs
            armor: If True, return ASCII-armored output

        Returns:
            Dictionary with encryption results
        """
        try:
            logger.info(
                f"Starting encryption for {len(recipient_keyids)} recipients")
            logger.debug(f"Data size: {len(data)} bytes")
            logger.debug(f"Recipient key IDs: {recipient_keyids}")

            encrypted_data = self.gpg.encrypt(
                data,
                recipient_keyids,
                armor=armor
            )

            if encrypted_data.ok:
                logger.info("Data encrypted successfully")
                return {
                    'success': True,
                    'data': str(encrypted_data),
                    'message': 'Data encrypted successfully'
                }
            else:
                logger.error(
                    f"Encryption failed with status: {encrypted_data.status}")
                logger.error(f"Encryption stderr: {encrypted_data.stderr}")
                return {
                    'success': False,
                    'message': f'Encryption failed: {encrypted_data.status}'
                }

        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            return {
                'success': False,
                'message': f'Error encrypting data: {str(e)}'
            }

    def decrypt_data(self, encrypted_data, passphrase: str = None) -> Dict[str, Any]:
        """
        Decrypt encrypted data.

        Args:
            encrypted_data: The encrypted data as string or bytes
            passphrase: Passphrase for the private key (if required)

        Returns:
            Dictionary with decryption results
        """
        try:
            logger.info("Starting data decryption")

            # Handle both bytes and string data
            if isinstance(encrypted_data, bytes):
                data_len = len(encrypted_data)
                unit = "bytes"
            else:
                data_len = len(encrypted_data)
                unit = "characters"

            logger.debug(f"Encrypted data length: {data_len} {unit}")
            logger.debug(
                f"Passphrase provided: {'Yes' if passphrase else 'No'}")

            decrypted_data = self.gpg.decrypt(
                encrypted_data, passphrase=passphrase)

            if decrypted_data.ok:
                logger.info("Data decrypted successfully")
                logger.debug(
                    f"Decrypted data size: {len(decrypted_data.data)} bytes")
                return {
                    'success': True,
                    'data': decrypted_data.data,
                    'message': 'Data decrypted successfully'
                }
            else:
                logger.error(
                    f"Decryption failed with status: {decrypted_data.status}")
                logger.error(f"Decryption stderr: {decrypted_data.stderr}")
                logger.debug(
                    f"Available private keys: {[key['keyid'] for key in self.list_keys(secret=True)]}")
                return {
                    'success': False,
                    'message': f'Decryption failed: {decrypted_data.status}'
                }

        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return {
                'success': False,
                'message': f'Error decrypting data: {str(e)}'
            }

    def encrypt_file(self, file_path: str, recipient_keyids: List[str],
                     output_path: str = None) -> Dict[str, Any]:
        """
        Encrypt a file for specified recipients.

        Args:
            file_path: Path to the file to encrypt
            recipient_keyids: List of recipient key IDs
            output_path: Output path for encrypted file (optional)

        Returns:
            Dictionary with encryption results
        """
        try:
            logger.info(f"Starting file encryption: {file_path}")
            logger.debug(f"Recipients: {recipient_keyids}")
            logger.debug(f"Output path: {output_path}")

            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {
                    'success': False,
                    'message': 'File not found'
                }

            file_size = os.path.getsize(file_path)
            logger.info(f"File size: {file_size} bytes")

            with open(file_path, 'rb') as f:
                file_data = f.read()

            logger.debug(
                f"File data read successfully, size: {len(file_data)} bytes")

            result = self.encrypt_data(file_data, recipient_keyids)

            if result['success'] and output_path:
                logger.info(f"Writing encrypted data to: {output_path}")
                with open(output_path, 'w') as f:
                    f.write(result['data'])
                result['output_path'] = output_path
                logger.info("Encrypted file saved successfully")

            return result

        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {str(e)}")
            return {
                'success': False,
                'message': f'Error encrypting file: {str(e)}'
            }

    def decrypt_file(self, file_path: str, passphrase: str = None,
                     output_path: str = None) -> Dict[str, Any]:
        """
        Decrypt an encrypted file.

        Args:
            file_path: Path to the encrypted file
            passphrase: Passphrase for the private key (if required)
            output_path: Output path for decrypted file (optional)

        Returns:
            Dictionary with decryption results
        """
        try:
            logger.info(f"Starting file decryption: {file_path}")
            logger.debug(
                f"Passphrase provided: {'Yes' if passphrase else 'No'}")
            logger.debug(f"Output path: {output_path}")

            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {
                    'success': False,
                    'message': 'File not found'
                }

            file_size = os.path.getsize(file_path)
            logger.info(f"Encrypted file size: {file_size} bytes")

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            logger.debug(
                f"Encrypted data read successfully, length: {len(encrypted_data)} bytes")

            result = self.decrypt_data(encrypted_data, passphrase)

            if result['success'] and output_path:
                logger.info(f"Writing decrypted data to: {output_path}")
                with open(output_path, 'wb') as f:
                    f.write(result['data'])
                result['output_path'] = output_path
                logger.info("Decrypted file saved successfully")

            return result

        except Exception as e:
            logger.error(f"Error decrypting file {file_path}: {str(e)}")
            return {
                'success': False,
                'message': f'Error decrypting file: {str(e)}'
            }

    def delete_key(self, keyid: str, secret: bool = False) -> Dict[str, Any]:
        """
        Delete a key by its ID.

        Args:
            keyid: The key ID or fingerprint to delete
            secret: If True, delete private key; if False, delete public key

        Returns:
            Dictionary with deletion results
        """
        try:
            result = self.gpg.delete_keys(keyid, secret=secret)

            if result.status == 'ok':
                return {
                    'success': True,
                    'message': f'Key {keyid} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to delete key: {result.status}'
                }

        except Exception as e:
            logger.error(f"Error deleting key {keyid}: {str(e)}")
            return {
                'success': False,
                'message': f'Error deleting key: {str(e)}'
            }
