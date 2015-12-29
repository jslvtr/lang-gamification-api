from passlib.context import CryptContext

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        all__vary_rounds=0.1,
        pbkdf2_sha256__default_rounds=8000
)