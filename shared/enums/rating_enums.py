from enum import Enum

class RatingSource(Enum):
    IMDB = "IMDB"
    ROTTEN_TOMATOES = "ROTTEN_TOMATOES"
    METACRITIC = "METACRITIC"

    @classmethod
    def from_omdb_source(cls, source: str) -> "RatingSource":
        source_mapping = {
            "Internet Movie Database": cls.IMDB,
            "Rotten Tomatoes": cls.ROTTEN_TOMATOES,
            "Metacritic": cls.METACRITIC
        }
        return source_mapping.get(source) 