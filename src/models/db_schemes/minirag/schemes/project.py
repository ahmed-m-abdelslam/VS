from .minirag_base import sqlalchemy_base
from sqlalchemy import Column, Integer, String, Text  # type: ignore

class Project(sqlalchemy_base):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, autoincrement=True)

