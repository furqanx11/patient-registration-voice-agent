import re


def normalize_phone(value: str | None) -> str | None:
    """Strip non-digits from a phone number and require exactly 10 digits.

    Handles common U.S. formatting like +1 (555) 123-4567.
    """
    if value is None:
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == 10 else None
