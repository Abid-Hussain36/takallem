from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.db.general_resource.resource_response import ResourceResponse
from app.db.database import get_db
from app.utils.auth import get_current_user_email
from app.services.resource_service import ResourceService
from app.utils.di import get_resource_service
from app.db.enums import ResourceType
from app.models.db.general_resource.polymorphic_resource_response import PolymorphicResource


resource_router = APIRouter()


@resource_router.get("/{id}", response_model=PolymorphicResource)
def get_resource(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service)
) -> PolymorphicResource:
    """
    Get full polymorphic resource by ID with all relationships loaded.
    """
    return service.get_resource(db, id)