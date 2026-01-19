from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.schemas.resource import Resource
from app.db.enums import ResourceType
from app.db.schemas.dialect_selection_dialects import dialect_selection_dialects
from app.models.db.general_resource.dialect_selection_response import DialectSelectionResponse

if TYPE_CHECKING:
    from app.db.schemas.dialect import DialectSchema


class DialectSelection(Resource):
    __tablename__ = "dialect_selections"

    id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    dialects: Mapped[List["DialectSchema"]] = relationship("DialectSchema", secondary=dialect_selection_dialects)

    __mapper_args__ = {
        "polymorphic_identity": ResourceType.DIALECT_SELECTION
    }

    def to_model(self) -> DialectSelectionResponse:
        return DialectSelectionResponse(
            id=self.id,
            resource_type=self.resource_type,
            dialects=[d.to_model() for d in self.dialects]
        )

