from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from shared.src.models.image_model import Images
from shared.src.models.link_model import Link, TextsWithLink, TextWithLink
from shared.src.models.location_model import Location
from shared.src.models.phone_model import Phones


class RoleEnum(str, Enum):
    PROFESSOR = "PROFESSOR"
    ASSOCIATE_PROFESSOR = "ASSOCIATE_PROFESSOR"
    ASSISTANT_PROFESSOR = "ASSISTANT_PROFESSOR"
    LECTURER = "LECTURER"
    RESEARCHER = "RESEARCHER"
    PHD_STUDENT = "PHD_STUDENT"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    OTHER = "OTHER"
    DR = "DR"
    PROF = "PROF"


class Contact(BaseModel):
    email: Optional[List[str]] = Field(None, description="List of email addresses")
    phone: Optional[Phones] = Field(None, description="Phone numbers including mobile")
    fax: Optional[Phones] = Field(None, description="Fax numbers")
    websites: Optional[List[Link]] = Field(None, description="Personal websites and profiles")


class Publication(BaseModel):
    title: str = Field(..., description="Title of the publication")
    year: int = Field(..., description="Year of publication")
    url: Optional[str] = Field(None, description="URL to the publication if available")
    authors: List[str] = Field(..., description="List of authors")
    venue: Optional[str] = Field(None, description="Publication venue or journal")


class Publications(RootModel):
    root: List[Publication] = Field(
        default_factory=list,
        description="List of publications"
    )


class ResearchInterest(BaseModel):
    title: str = Field(..., description="Title of the research interest")
    description: Optional[str] = Field(None, description="Detailed description of the research interest")


class ResearchInterests(RootModel):
    root: List[ResearchInterest] = Field(
        default_factory=list,
        description="List of research interests"
    )


class Thesis(BaseModel):
    title: str = Field(..., description="Title of the thesis")
    description: str = Field(..., description="Description of the thesis topic")
    type: str = Field(..., description="Type of thesis (Bachelor, Master, PhD)")
    requirements: Optional[str] = Field(None, description="Requirements for the thesis")
    deadline: Optional[datetime] = Field(None, description="Application deadline if applicable")


class Theses(RootModel):
    root: List[Thesis] = Field(
        default_factory=list,
        description="List of available theses"
    )


class Person(BaseModel):
    id: str = Field(..., description="Unique identifier for the person")
    title: str = Field(..., description="Title of the person")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    role: RoleEnum = Field(..., description="Role at the university")
    contact: Contact = Field(..., description="Contact information")
    location: Optional[Location] = Field(None, description="Office location and address")
    about: Optional[str] = Field(None, description="About me section")
    publications: Optional[Publications] = Field(None, description="List of publications")
    research_interests: Optional[ResearchInterests] = Field(None, description="Research interests")
    images: Images = Field(default_factory=Images, description="Profile images")
    theses: Optional[Theses] = Field(None, description="Available theses")
    hash: str = Field(..., description="Hash for tracking changes")
    url: Optional[str] = Field(None, description="Personal webpage URL")
