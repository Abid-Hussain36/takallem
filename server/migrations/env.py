import os
from dotenv import load_dotenv

load_dotenv()

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.db.database import Base
from app.db.schemas.user import User
from app.db.schemas.user_course_progress import UserCourseProgress
from app.db.schemas.resource import Resource
from app.db.schemas.module import Module
from app.db.schemas.vocab_word import VocabWord
from app.db.schemas.vocab_lecture import VocabLecture
from app.db.schemas.letter_writing_sequence import LetterWritingSequence
from app.db.schemas.vocab_speaking_problem import VocabSpeakingProblem
from app.db.schemas.vocab_speaking_problem_set import VocabSpeakingProblemSet
from app.db.schemas.vocab_speaking_problem_sets import VocabSpeakingProblemSets
from app.db.schemas.vocab_speaking_problem_word import vocab_speaking_problem_word
from app.db.schemas.vocab_listening_problem import VocabListeningProblem
from app.db.schemas.vocab_listening_problem_set import VocabListeningProblemSet
from app.db.schemas.vocab_listening_problem_sets import VocabListeningProblemSets
from app.db.schemas.vocab_reading_problem import VocabReadingProblem
from app.db.schemas.vocab_reading_problem_set import VocabReadingProblemSet
from app.db.schemas.vocab_reading_problem_sets import VocabReadingProblemSets
from app.db.schemas.dictation_problem import DictationProblem
from app.db.schemas.dictation_problem_set import DictationProblemSet
from app.db.schemas.discrimination_problem import DiscriminationProblem
from app.db.schemas.discrimination_problem_set import DiscriminationProblemSet
from app.db.schemas.letter_recognition_problem import LetterRecognitionProblem
from app.db.schemas.letter_recognition_problem_set import LetterRecognitionProblemSet
from app.db.schemas.letter_joining_problem import LetterJoiningProblem
from app.db.schemas.letter_joining_problem_set import LetterJoiningProblemSet
from app.db.schemas.letter_writing_problem import LetterWritingProblem
from app.db.schemas.letter_writing_problem_set import LetterWritingProblemSet
from app.db.schemas.word_pronounciation_problem import WordPronounciationProblem
from app.db.schemas.word_pronounciation_problem_set import WordPronounciationProblemSet
from app.db.schemas.letter_pronounciation_problem import LetterPronounciationProblem
from app.db.schemas.letter_speaking_lecture import LetterSpeakingLecture
from app.db.schemas.letter_writing_lecture import LetterWritingLecture
from app.db.schemas.info_lecture import InfoLecture
from app.db.schemas.reading_comprehension_text import ReadingComprehensionText
from app.db.schemas.reading_comprehension_mcq_problem import ReadingComprehensionMCQProblem
from app.db.schemas.reading_comprehension_mcq_problem_set import ReadingComprehensionMCQProblemSet
from app.db.schemas.reading_comprehension_writing_problem import ReadingComprehensionWritingProblem
from app.db.schemas.reading_comprehension_writing_problem_set import ReadingComprehensionWritingProblemSet
from app.db.schemas.language import Language
from app.db.schemas.course import Course
from app.db.schemas.dialect import Dialect
from app.db.schemas.dialect_selection import DialectSelection
from app.db.schemas.dialect_selection_dialects import dialect_selection_dialects

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from environment variable
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
