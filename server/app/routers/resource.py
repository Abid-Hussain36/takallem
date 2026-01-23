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


@resource_router.get("/base/{id}", response_model=ResourceResponse)
def get_resource_base(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service)
) -> ResourceResponse:
    """
    Get basic resource information (id and resource_type only).
    Use this for lightweight queries when you don't need full resource data.
    """
    return service.get_resource_by_id(db, id)


@resource_router.get("/{id}", response_model=PolymorphicResource)
def get_resource(
    id: int,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service)
) -> PolymorphicResource:
    """
    Get full polymorphic resource by ID with all relationships loaded.
    
    Returns the complete resource data (lectures, problem sets, etc.) 
    with all nested relationships (vocab words, problems, dialects, etc.).
    
    SQLAlchemy automatically returns the correct subclass based on resource_type.
    """
    return service.get_polymorphic_resource(db, id)


@resource_router.get("/type/{id}/{resource_type}", response_model=PolymorphicResource)
def get_resource_by_type(
    id: int,
    resource_type: ResourceType,
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
    service: ResourceService = Depends(get_resource_service)
) -> PolymorphicResource:
    """
    Get full polymorphic resource by ID and specific type.
    
    Alternative endpoint when you know the resource_type upfront.
    Provides better type-specific optimization and validation.
    
    Use this when:
    - You already know the resource_type
    - You want to validate the resource is of a specific type
    - You want slightly better query performance
    """
    return service.get_polymorphic_resource_by_type(db, id, resource_type)