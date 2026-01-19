from typing import List, TYPE_CHECKING
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import ResourceType
from app.models.db.general_resource.resource_response import ResourceResponse

if TYPE_CHECKING:
    from app.db.schemas.module import Module


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

    def to_model(self) -> ResourceResponse:
        return ResourceResponse(
            id=self.id,
            resource_type=self.resource_type
        )
