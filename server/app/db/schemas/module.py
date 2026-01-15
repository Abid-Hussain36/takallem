from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableCourse
from app.models.db.general_resource.module_response import ModuleResponse

if TYPE_CHECKING:
    from app.db.schemas.resource import Resource


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)  # PK

    course: Mapped[AvailableCourse] = mapped_column(Enum(AvailableCourse))
    unit: Mapped[str] = mapped_column(String)
    section: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    number: Mapped[int] = mapped_column()

    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"))

    # Relationship
    resource: Mapped["Resource"] = relationship(back_populates="module")

    __table_args__ = (
        UniqueConstraint("course", "unit", "section", "number", name="uq_course_unit_section_number"),
        Index("idx_course_unit_section_number", "course", "unit", "section", "number")
    )

    def to_model(self) -> ModuleResponse:
        return ModuleResponse(
            id=self.id,
            course=self.course,
            unit=self.unit,
            section=self.section,
            title=self.title,
            number=self.number,
            resource=self.resource.to_model()  # Include the actual polymorphic resource
        )
