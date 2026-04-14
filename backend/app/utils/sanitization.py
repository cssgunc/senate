"""HTML sanitization utilities."""

import bleach

# Allowed HTML tags for rich text content
ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "ol",
    "ul",
    "li",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    "img",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "code",
    "pre",
]

# Allowed attributes for HTML tags
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "img": ["src", "alt", "title", "width", "height"],
    "table": ["border", "cellpadding", "cellspacing"],
}


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Allows safe HTML tags and attributes commonly used in rich text editors.
    """
    if not content:
        return ""
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
