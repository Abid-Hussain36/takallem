from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.db.schemas.resource import Resource
from app.models.db.general_resource.polymorphic_resource_response import PolymorphicResource


class ResourceService:
    def get_resource(self, db: Session, id: int) -> PolymorphicResource:
        """
        Fetches a polymorphic resource by ID with all relationships eagerly loaded.        
        """
        # Query from base Resource table - SQLAlchemy will return the correct subclass
        # based on the polymorphic_identity (resource_type)
        # Eagerly load all relationships to avoid lazy loading issues
        # selectinload('*') loads all relationships in separate SELECT statements
        resource = db.query(Resource).filter(Resource.id == id).options(selectinload('*')).first()
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with id {id} not found."
            )
        
        # The to_model() method will be called on the correct subclass
        # (e.g., VocabLecture, InfoLecture, etc.) with all relationships loaded
        return resource.to_model()