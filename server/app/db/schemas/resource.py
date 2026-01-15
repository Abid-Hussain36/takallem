from typing import List
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import ResourceType
from app.models.db.general_resource.resource_response import ResourceResponse


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    # Depending on what value this is set, we get back the corresponding subclass (which subclass to instantiate)
    # The resource table just contains a bunch of rows with ID and a subclass object
    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType))  # Polymorphic types

    __mapper_args__ = {
        "polymorphic_on": resource_type,  # This determines which subclasses we can create
        "polymorphic_identity": None  # We cant get back just a plain resource object, only a subclass object
    }

    # Relationships
    module: Mapped[List["Module"]] = relationship(back_populates="resource", cascade="all, delete-orphan")

    def to_model(self) -> ResourceResponse:
        """
        This method should be overridden by subclasses to return their specific response types.
        The base Resource class returns a minimal ResourceResponse.
        """
        return ResourceResponse(
            id=self.id,
            resource_type=self.resource_type
        )
