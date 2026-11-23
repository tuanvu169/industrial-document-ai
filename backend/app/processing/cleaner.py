import re
import unicodedata

_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")
_MULTI_NL = re.compile(r"\n{3,}")
_SPACES = re.compile(r"[ \t\u00a0]+")


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\x00", "")
    text = _HYPHEN_BREAK.sub(r"\1\2", text)  # join words hyphenated across lines
    text = _SPACES.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return _MULTI_NL.sub("\n\n", text).strip()
