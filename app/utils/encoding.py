import base64
from builtins import bytes


def encode_base64(text: str) -> str:
    text_bytes: bytes = text.encode("utf-8")
    base64_bytes: bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode("utf-8")


def decode_base64(encoded_text: str) -> str:
    base64_bytes: bytes = encoded_text.encode("utf-8")
    text_bytes: bytes = base64.b64decode(base64_bytes)
    return text_bytes.decode("utf-8")
