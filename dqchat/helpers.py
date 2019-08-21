from cryptography.fernet import Fernet
import base64
from diffiehellman.diffiehellman import DiffieHellman


def _shared_key_to_fernet(shared_key: str) -> Fernet:
    return Fernet(
        base64.urlsafe_b64encode(bytes(
            shared_key[:32],
            "utf-8"
        ))
    )


def get_shared_key(diffieh: DiffieHellman, other_public_key: int) -> Fernet:
    diffieh.generate_shared_secret(other_public_key, echo_return_key=True)
    return _shared_key_to_fernet(diffieh.shared_key)
