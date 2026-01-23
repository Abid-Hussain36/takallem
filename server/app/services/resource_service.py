from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload, joinedload
from app.models.db.general_resource.resource_response import ResourceResponse
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.models.db.general_resource.polymorphic_resource_response import PolymorphicResource
from app.utils.resource_map import RESOURCE_TYPE_TO_CLASS


class ResourceService:
    def get_polymorphic_resource(self, db: Session, id: int) -> PolymorphicResource:
        """
        Fetches a polymorphic resource by ID with all relationships eagerly loaded.
        SQLAlchemy's polymorphic loading automatically returns the correct subclass.
        
        This uses selectinload('*') to eagerly load all relationships defined on the resource.
        """
        # Query from base Resource table - SQLAlchemy will return the correct subclass
        # based on the polymorphic_identity (resource_type)
        # Eagerly load all relationships to avoid lazy loading issues
        # selectinload('*') loads all relationships in separate SELECT statements
        polymorphic_resource = db.query(Resource).filter(Resource.id == id).options(selectinload('*')).first()
        
        if not polymorphic_resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with id {id} not found."
            )
        
        # The to_model() method will be called on the correct subclass
        # (e.g., VocabLecture, InfoLecture, etc.) with all relationships loaded
        return polymorphic_resource.to_model()