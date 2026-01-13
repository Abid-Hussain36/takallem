from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.enums import AvailableDialect
from app.models.db.general_resource.dialect_response import DialectResponse


class Dialect(Base):
    __tablename__ = "dialects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True) # PK

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id", ondelete="CASCADE")) # FK

    dialect: Mapped[AvailableDialect] = mapped_column(Enum(AvailableDialect))
    image: Mapped[str] = mapped_column(String)
    text_color: Mapped[str] = mapped_column(String)

    # Relationships
    language: Mapped["Language"] = relationship(back_populates="dialects")

    def to_model(self) -> DialectResponse:
        return DialectResponse(
            id=self.id,
            dialect=self.dialect,
            image=self.image,
            text_color=self.text_color
        )