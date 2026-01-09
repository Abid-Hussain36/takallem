from sqlalchemy import Column, ForeignKey, Integer, Table
from app.db.database import Base

# Association Table for Many to Many between VocabSpeakingProblem and VocabWord
vocab_speaking_problem_word = Table(
    "vocab_speaking_problem_words",
    Base.metadata, # Specifies that this is to be made in the same schema as the rest of the tables
    Column("vocab_speaking_problem_id", Integer, ForeignKey("vocab_speaking_problems.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    Column("vocab_word_id", Integer, ForeignKey("vocab_words.id", ondelete="CASCADE"), primary_key=True, nullable=False),
)