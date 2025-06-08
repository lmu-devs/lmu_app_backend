import re
from pydantic import BaseModel
from typing import List, Tuple, Optional


class TreePath(BaseModel):
    path: List[str]


class Lecture(BaseModel):
    publish_id: int
    title: str
    tree_paths: Optional[List[TreePath]]

    @classmethod
    def from_tuple(cls, raw: Tuple[str, str, List[str]]) -> "Lecture":
        title, url, paths = raw
        match = re.search(r"publishid=(\d+)", url)
        publish_id = int(match.group(1)) if match else None
        tree_paths = [TreePath(path=p) for p in paths] if paths else None
        return cls(title=title, publish_id=publish_id, tree_paths=tree_paths)


"""
https://lsf.verwaltung.uni-muenchen.de/qisserver/rds?state=verpublish&status=init&
vmfile=no&publishid=1075174&moduleCall=webInfo&publishConfFile=webInfo&
publishSubDir=veranstaltung
"""
