from enum import Enum


class LetterPosition(str, Enum):
    BEGINNING = "beginning"
    MIDDLE = "middle"
    END = "end"
    STANDALONE = "standalone"