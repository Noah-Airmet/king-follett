"""Small HTML helpers.

No template engine: the site has five page shapes and they are easier to read
as Python than as a dialect of Python embedded in strings. The only rule that
matters here is that every piece of text from ``data/`` or ``transcripts/``
passes through :func:`esc` before it reaches the page.
"""

from __future__ import annotations

from html import escape

#: Elements that never take a closing tag.
VOID = {"br", "hr", "img", "input", "link", "meta", "source"}


def esc(text: object) -> str:
    """Escape text for element content and double-quoted attributes."""
    return escape(str(text), quote=True)


def attrs(mapping: dict[str, object]) -> str:
    """Render an attribute mapping.

    ``True`` renders a bare boolean attribute; ``False`` and ``None`` drop it.
    Underscores in names become hyphens so ``data_section`` writes
    ``data-section``.
    """
    out = []
    for key, value in mapping.items():
        if value is False or value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        if value is True:
            out.append(f" {name}")
        else:
            out.append(f' {name}="{esc(value)}"')
    return "".join(out)


def tag(name: str, *children: str, **attributes: object) -> str:
    """One element. Children are inserted as-is, so escape them first."""
    opening = f"<{name}{attrs(attributes)}>"
    if name in VOID:
        return opening
    return f"{opening}{''.join(children)}</{name}>"


def join(*parts: str) -> str:
    return "".join(parts)
