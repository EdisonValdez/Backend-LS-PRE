import logging
from datetime import datetime, timedelta
from io import BytesIO

import pyotp
import qrcode
from qrcode.image.svg import SvgImage


class TwoFAProvider:
    logger = logging.getLogger(__name__)

    def __init__(self, secret=None, delay: int = None):
        if secret is None:
            secret = pyotp.random_base32()
        self.secret = secret
        self.delay = delay
        self.totp = pyotp.TOTP(secret)

    def generate_token(self):
        return self.totp.now()

    def valid(self, token: str):
        try:
            valid_now = self.totp.verify(token)
            return valid_now or bool(
                self.delay and self.totp.verify(token, for_time=datetime.now() - timedelta(seconds=self.delay))
            )
        except Exception as e:
            self.logger.error('Error checking OTP code', exc_info=e)
        return False

    def qr_code(self, issuer, username):
        uri = self.totp.provisioning_uri(username, issuer)
        qr = qrcode.make(uri, image_factory=SvgImage)
        stream = BytesIO()
        qr.save(stream)
        return stream.getvalue()
