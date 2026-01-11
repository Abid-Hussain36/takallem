from sqlalchemy import Column, ForeignKey, Integer, Table
from app.db.database import Base


# Association table for many-to-many relationship between DialectSelection and Dialect
dialect_selection_dialects = Table(
    "dialect_selection_dialects",
    Base.metadata,
    Column("dialect_selection_id", Integer, ForeignKey("dialect_selections.id", ondelete="CASCADE"), primary_key=True),
    Column("dialect_id", Integer, ForeignKey("dialects.id", ondelete="CASCADE"), primary_key=True)
)