import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher


class BcryptHasher(BasePasswordHasher):
    algorithm = "bcrypt"

    def encode(self, password, salt=None, iterations=None):
        assert password is not None
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return f"{self.algorithm}${hashed.decode()}"

    def verify(self, password, encoded):
        algorithm, hashed = encoded.split('$', 1)
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def safe_summary(self, encoded):
        algorithm, hashed = encoded.split('$', 1)
        return {
            "************************": "",
        }

    def must_update(self, encoded):
        return False
