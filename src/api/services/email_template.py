import re
from pathlib import Path

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def load_template(filename: str) -> str:
    return (_TEMPLATE_DIR / filename).read_text(encoding="utf-8")


def inject(template: str, data: dict) -> str:
    """Replace {{key}} placeholders with values from data. Unknown keys are left as-is."""
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return str(data[key]) if key in data else match.group(0)

    return re.sub(r"\{\{(\w+)\}\}", _replace, template)


def parse_subject_body(template: str) -> tuple[str, str]:
    """Split template into (subject_template, body_template).

    Expected format:
        Subject: <subject text>
        <blank line>
        <body text...>
    """
    lines = template.splitlines()
    if not lines or not lines[0].startswith("Subject: "):
        raise ValueError("Email template must start with 'Subject: '")

    subject = lines[0][len("Subject: "):]

    # Find first blank line after the subject
    for i in range(1, len(lines)):
        if lines[i].strip() == "":
            body = "\n".join(lines[i + 1:])
            return subject, body

    return subject, ""
