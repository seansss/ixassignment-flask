import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime

class Base(DeclarativeBase):
    pass

class alcProject(Base):
    __tablename__ = "Projects"

    Id: Mapped[str] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100))
    StartDate: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow())
    Files: Mapped[List["alcFile"]] = relationship(
        back_populates="Project", cascade="all, delete-orphan"
    )
    Users: Mapped[List["alcUser"]] = relationship(secondary='ProjectUsers')

    def __repr__(self) -> str:
        return f"Project(Id={self.Id!r}, Name={self.Name!r})"

class alcFile(Base):
    __tablename__ = "IXFiles"

    Id: Mapped[str] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(String(100))
    Type: Mapped[str] = mapped_column(String(100))
    FilePath: Mapped[str] = mapped_column(String(1000))
    ProjectId: Mapped[str] = mapped_column(ForeignKey("Projects.Id")) 
    Project: Mapped["alcProject"] = relationship(back_populates="Files") 

    def __repr__(self) -> str: 
        return f"alcFile(Id={self.Id!r}, Name={self.Name!r}, Type={self.Type!r}, FilePath={self.FilePath!r})" 

class alcUser(Base): 
    __tablename__ = "Users" 

    Id: Mapped[str] = mapped_column(primary_key=True) 
    Name: Mapped[str] = mapped_column(String(100)) 
    Email: Mapped[str] = mapped_column(String(100)) 
    Projects: Mapped[List["alcProject"]] = relationship(secondary='ProjectUsers')

    def __repr__(self) -> str: 
        return f"alcUser(Id={self.Id!r}, Name={self.Name!r})" 

class alcProjectUser(Base): 
    __tablename__ = "ProjectUsers" 

    Id: Mapped[str] = mapped_column(primary_key=True) 
    UserId: Mapped[str] = mapped_column(ForeignKey("Users.Id")) 
    ProjectId: Mapped[str] = mapped_column(ForeignKey("Projects.Id")) 

    def __repr__(self) -> str: 
        return f"alcUser(Id={self.Id!r}, UserId={self.UserId!r}, ProjectId={self.ProjectId!r})" 

