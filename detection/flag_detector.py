import re


def detect_flag(text: str):
    """
    Detect common CTF flag formats.
    """

    patterns = [
        r"flag\{.*?\}",
        r"CTF\{.*?\}",
        r"OTW\{.*?\}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return None