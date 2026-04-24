import re
from fastapi import status, HTTPException

email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
username_regex = re.compile(r'^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$', re.IGNORECASE)


def check_username_or_email(username_or_email):
    if not isinstance(username_or_email, str) or not username_or_email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email yoki username kiritilmadi"
        )

    username_or_email = username_or_email.strip()

    if re.fullmatch(email_regex, username_or_email):
        return 'email'
    elif re.fullmatch(username_regex, username_or_email):
        return 'username'

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Login yoki parol xato"
    )