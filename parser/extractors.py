import re
from typing import Set


EMAIL_REGEX = re.compile(
    r'''
    [a-zA-Z0-9._%+-]+
    @
    [a-zA-Z0-9.-]+
    \.[a-zA-Z]{2,}
    ''',
    re.VERBOSE,
)

PHONE_REGEX = re.compile(
    r'''
    (?:
        \+?\d{1,3}[\s\-()]*
    )?
    (?:
        \d[\s\-()]*
    ){7,}
    ''',
    re.VERBOSE,
)


def extract_emails(text: str) -> Set[str]:
    '''
    Extract email addresses from raw text.
    '''
    return {match.group(0) for match in EMAIL_REGEX.finditer(text)}


def extract_phones(text: str) -> Set[str]:
    '''
    Extract phone numbers from raw text.
    '''
    raw_phones = {match.group(0) for match in PHONE_REGEX.finditer(text)}
    return {_normalize_phone(phone) for phone in raw_phones}


def _normalize_phone(phone: str) -> str:
    '''
    Normalize phone number by removing spaces and separators.
    '''
    return re.sub(r'[^\d+]', '', phone)
