from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging
from models import Tag
from Schemas.tags import TagResponse, TagCreate
from database import get_db

# Configure logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2")

@router.post("/tags/", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating tag with name: {tag.name}")
    db_tag = Tag(name=tag.name)
    
    try:
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        logger.info(f"Tag created successfully: {db_tag.id} - {db_tag.name}")
        return db_tag
    except IntegrityError:
        logger.warning(f"Tag with name '{tag.name}' already exists.")
        db.rollback()
        raise HTTPException(status_code=400, detail="Tag with this name already exists.")
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the tag.")

@router.get("/tags/search", response_model=List[TagResponse])
def search_tags(query: Optional[str] = None, db: Session = Depends(get_db)):
    logger.info(f"Searching tags with query: {query}")
    if query:
        tags = db.query(Tag).filter(Tag.name.ilike(f"%{query}%")).all()
    else:
        tags = db.query(Tag).all()
    logger.info(f"Found {len(tags)} tags")
    return tags



