"""
Two-Factor Authentication Service

Provides functionality for setting up and verifying TOTP-based 2FA.
"""

import pyotp
import qrcode
import secrets
import base64
from io import BytesIO
from typing import Tuple, List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TwoFactorService:
    """Service for managing two-factor authentication"""

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random base32 secret for TOTP

        Returns:
            str: Base32-encoded secret
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(email: str, secret: str, issuer: str = "OppGrid") -> str:
        """
        Generate QR code for authenticator app setup

        Args:
            email: User's email address
            secret: TOTP secret
            issuer: Application name

        Returns:
            str: Base64-encoded QR code image
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name=issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_otp(secret: str, otp_code: str) -> bool:
        """
        Verify an OTP code against the secret

        Args:
            secret: User's TOTP secret
            otp_code: 6-digit OTP code to verify

        Returns:
            bool: True if OTP is valid, False otherwise
        """
        if not secret or not otp_code:
            return False

        totp = pyotp.TOTP(secret)
        # Allow for 1 interval drift (30 seconds before/after)
        return totp.verify(otp_code, valid_window=1)

    @staticmethod
    def generate_backup_codes(count: int = 10) -> Tuple[List[str], str]:
        """
        Generate backup codes for account recovery

        Args:
            count: Number of backup codes to generate

        Returns:
            Tuple of (plain codes list, encrypted codes string)
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                          for _ in range(8))
            codes.append(code)

        # Hash the codes for storage
        hashed_codes = [pwd_context.hash(code) for code in codes]
        encrypted_string = ",".join(hashed_codes)

        return codes, encrypted_string

    @staticmethod
    def verify_backup_code(stored_codes: str, provided_code: str) -> Tuple[bool, str]:
        """
        Verify a backup code and remove it from the list

        Args:
            stored_codes: Comma-separated hashed backup codes
            provided_code: Plain backup code provided by user

        Returns:
            Tuple of (is_valid, updated_codes_string)
        """
        if not stored_codes or not provided_code:
            return False, stored_codes

        codes_list = stored_codes.split(",")
        remaining_codes = []
        is_valid = False

        for hashed_code in codes_list:
            if not is_valid and pwd_context.verify(provided_code, hashed_code):
                # Code matches, don't add it back (single use)
                is_valid = True
            else:
                # Keep this code
                remaining_codes.append(hashed_code)

        updated_string = ",".join(remaining_codes) if remaining_codes else None
        return is_valid, updated_string

    @staticmethod
    def get_remaining_backup_codes_count(stored_codes: str) -> int:
        """
        Get the number of remaining backup codes

        Args:
            stored_codes: Comma-separated hashed backup codes

        Returns:
            int: Number of remaining codes
        """
        if not stored_codes:
            return 0
        return len([c for c in stored_codes.split(",") if c.strip()])


two_factor_service = TwoFactorService()
