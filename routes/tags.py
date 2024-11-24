from fastapi import APIRouter, Depends, HTTPException
from mongoengine import DoesNotExist, NotUniqueError
from typing import List, Optional
import logging
from models.models import Tag
from schemas.tags import TagResponse, TagCreate
from database.database import db
from utils.auth_utils import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3")

@router.post("/tags/", response_model=TagResponse)
def create_tag(tag: TagCreate, db=Depends(db), current_user=Depends(get_current_user)):
    logger.info(f"Creating tag with name: {tag.name}")
    db_tag = Tag(name=tag.name, user_id=current_user.id)
    
    try:
        db_tag.save()
        logger.info(f"Tag created successfully: {db_tag.id} - {db_tag.name}")
        return TagResponse(
            id=str(db_tag.id),
            name=db_tag.name
        )
    except NotUniqueError:
        logger.warning(f"Tag with name '{tag.name}' already exists.")
        raise HTTPException(status_code=400, detail="Tag with this name already exists.")
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the tag.")

@router.get("/tags/search", response_model=List[TagResponse])
def search_tags(query: Optional[str] = None):
    logger.info(f"Searching tags with query: {query}")
    if query:
        tags = Tag.objects(name__icontains=query)
    else:
        tags = Tag.objects()
    logger.info(f"Found {len(tags)} tags")
    return [TagResponse(
        id=str(tag.id),
        name=tag.name
    ) for tag in tags]

@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: str, current_user=Depends(get_current_user)):
    logger.info(f"Attempting to delete tag with ID: {tag_id}")
    try:
        tag_to_delete = Tag.objects.get(id=tag_id, user_id=current_user.id)
        tag_to_delete.delete()
        logger.info(f"Tag with ID {tag_id} deleted successfully.")
    except DoesNotExist:
        logger.warning(f"Tag with ID {tag_id} not found.")
        raise HTTPException(status_code=404, detail="Tag not found.")
    return {"detail": "Tag deleted successfully"}


