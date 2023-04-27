import typing
from datetime import timedelta

from django.core.cache import cache

from djangoblog.utils import send_email

_code_ttl = timedelta(minutes=5)


def send_verify_email(to_mail: str, code: str, subject: str = "email verification code"):
    """Send reset password verification code
    Args:
        to_mail: accept email
        subject:subject
        code:verification code
    """
    html_content = f"You are resetting your password, the verification code is：{code}, Valid within 5 minutes, please keep it safe"
    send_email([to_mail], subject, html_content)


def verify(email: str, code: str) -> typing.Optional[str]:
    """Verify that the code is valid
    Args:
        email: request email
        code:verification code
    Return:
        request eReturns error str if there is an errormail
    Node:
        The error handling here is unreasonable, raise should be used to throw
        No test caller also needs to handle the error
    """
    cache_code = get_code(email)
    if cache_code != code:
        return "Verification code error"


def set_code(email: str, code: str):
    """set code"""
    cache.set(email, code, _code_ttl.seconds)


def get_code(email: str) -> typing.Optional[str]:
    """get code"""
    return cache.get(email)
