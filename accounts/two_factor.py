"""
SafeZone AI — Two-Factor Authentication (2FA)
TOTP-based 2FA using pyotp + QR code generation
"""
import pyotp
import qrcode
import io
import base64
from django.conf import settings


def generate_totp_secret() -> str:
    """Generate a new TOTP secret key for a user."""
    return pyotp.random_base32()


def get_totp_uri(user, secret: str) -> str:
    """Generate otpauth URI for QR code."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name   = user.email or user.username,
        issuer_name = getattr(settings, 'OTP_TOTP_ISSUER', 'SafeZone AI')
    )


def generate_qr_code(totp_uri: str) -> str:
    """Generate QR code as base64 PNG string."""
    try:
        qr = qrcode.QRCode(version=1, box_size=6, border=3)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img     = qr.make_image(fill_color='black', back_color='white')
        buf     = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except ImportError:
        return ''


def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP token. Returns True if valid."""
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    except Exception:
        return False


def get_backup_codes(n: int = 8) -> list:
    """Generate n backup codes for account recovery."""
    import secrets
    return [secrets.token_hex(4).upper() for _ in range(n)]
