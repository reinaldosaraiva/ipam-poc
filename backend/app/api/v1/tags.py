"""Tags API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.tag import TagCreate, TagResponse, TagUpdate
from app.utils.slug import generate_slug

router = APIRouter()


@router.get("/", response_model=list[TagResponse])
async def list_tags(
    limit: int = 100,
    offset: int = 0,
) -> list[TagResponse]:
    """List all tags."""
    nb = get_netbox_client()

    tags = nb.extras.tags.filter(limit=limit, offset=offset)

    return [
        TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            description=tag.description or "",
            color=tag.color or "9e9e9e",
            created=tag.created,
            last_updated=tag.last_updated,
        )
        for tag in tags
    ]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int) -> TagResponse:
    """Get a specific tag by ID."""
    nb = get_netbox_client()
    tag = nb.extras.tags.get(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found",
        )

    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
        description=tag.description or "",
        color=tag.color or "9e9e9e",
        created=tag.created,
        last_updated=tag.last_updated,
    )


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(tag_data: TagCreate) -> TagResponse:
    """Create a new tag."""
    nb = get_netbox_client()

    slug = tag_data.slug or generate_slug(tag_data.name)

    data = {
        "name": tag_data.name,
        "slug": slug,
        "description": tag_data.description,
        "color": tag_data.color,
    }

    try:
        tag = nb.extras.tags.create(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
        description=tag.description or "",
        color=tag.color or "9e9e9e",
        created=tag.created,
        last_updated=tag.last_updated,
    )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int) -> None:
    """Delete a tag."""
    nb = get_netbox_client()
    tag = nb.extras.tags.get(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found",
        )

    try:
        tag.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
