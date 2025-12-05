"""Slug generation utilities with Portuguese accent handling."""

import re
import unicodedata


def generate_slug(name: str, slug: str | None = None) -> str:
    """
    Generate a slug from a name, handling Portuguese accents.

    Args:
        name: The name to convert to slug
        slug: Optional pre-defined slug (returned as-is if provided)

    Returns:
        A URL-safe slug string

    Examples:
        >>> generate_slug("São Paulo")
        'sao-paulo'
        >>> generate_slug("Produção Norte")
        'producao-norte'
        >>> generate_slug("Área Técnica")
        'area-tecnica'
    """
    if slug:
        return slug

    # Normalize unicode and remove accents
    normalized = unicodedata.normalize("NFKD", name)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    # Convert to lowercase
    lowercase = ascii_text.lower()

    # Replace spaces and special chars with hyphens
    slug_text = re.sub(r"[^a-z0-9]+", "-", lowercase)

    # Remove leading/trailing hyphens
    slug_text = slug_text.strip("-")

    # Remove consecutive hyphens
    slug_text = re.sub(r"-+", "-", slug_text)

    return slug_text


def validate_slug(slug: str) -> bool:
    """
    Validate that a slug follows the correct format.

    Args:
        slug: The slug to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return bool(re.match(pattern, slug))
