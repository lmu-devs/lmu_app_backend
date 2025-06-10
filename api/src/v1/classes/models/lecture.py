import re
from pydantic import BaseModel, RootModel
from typing import List, Tuple, Optional


class TreePath(BaseModel):
    path: List[str]


class Lecture(BaseModel):
    publish_id: int
    title: str
    tree_paths: Optional[List[TreePath]]

    @classmethod
    def from_tuple(cls, raw: Tuple[str, str, List[List[str]]]) -> "Lecture":
        title, url, paths = raw
        match = re.search(r"publishid=(\d+)", url)
        publish_id = int(match.group(1)) if match else None
        tree_paths = [TreePath(path=p) for p in paths] if paths else None
        return cls(title=title, publish_id=publish_id, tree_paths=tree_paths)


class Lectures(RootModel):
    root: List[Lecture] | List[Lecture] = []

    @classmethod
    def from_raw(cls, raw: List[Tuple[str, str, List[List[str]]]]) -> "Lectures":
        return cls(root=[Lecture.from_tuple(item) for item in raw])
