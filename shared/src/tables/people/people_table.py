from sqlalchemy import Column, ForeignKey, JSON, String, Integer, Text
from sqlalchemy.orm import relationship
from shared.src.core.database import Base

class PeopleTable(Base):
    __tablename__ = "people"
    
    # Basic identification
    id = Column(String, primary_key=True)  # We'll generate this from profile_url or name
    profile_url = Column(String, nullable=True)  # LSF profile URL
    
    # Basic info from crawler
    name = Column(String, nullable=False)  # Full name from crawler
    first_name = Column(String, nullable=True)  # From basic_info
    last_name = Column(String, nullable=True)   # From basic_info
    gender = Column(String, nullable=True)      # From basic_info
    title = Column(String, nullable=True)       # From basic_info
    academic_degree = Column(String, nullable=True)  # From basic_info
    employment_status = Column(String, nullable=True)  # From basic_info
    name_suffix = Column(String, nullable=True)        # From basic_info
    status = Column(String, nullable=True)              # From basic_info
    note = Column(Text, nullable=True)                  # From basic_info
    office_hours = Column(String, nullable=True)       # From basic_info (Sprechzeit)
    
    # Contact information
    email = Column(String, nullable=True)    # Single email from crawler
    address = Column(String, nullable=True)  # Dienstadresse from crawler
    
    # Faculty relationship
    faculty = Column(String, nullable=True)  # Faculty name from crawler
    faculty_id = Column(String, ForeignKey("faculties.id"), nullable=True)  # Will be mapped later
    
    # Crawler metadata
    hash = Column(String, nullable=True)  # For change detection
    
    # Relationships
    roles = relationship("PeopleRoleTable", back_populates="person", cascade="all, delete-orphan")
    courses = relationship("PeopleCoursesTable", back_populates="person", cascade="all, delete-orphan")


class PeopleRoleTable(Base):
    __tablename__ = "people_roles"
    
    id = Column(String, primary_key=True)
    person_id = Column(String, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    
    # Role information from crawler
    institution = Column(String, nullable=True)      # From roles array
    role = Column(String, nullable=True)             # From roles array  
    institution_url = Column(String, nullable=True)  # From roles array
    
    # LSF role information
    lsf_role_id = Column(Integer, nullable=True)     # From role.id in crawler
    lsf_role_name = Column(String, nullable=True)    # From role.name in crawler
    
    person = relationship("PeopleTable", back_populates="roles")


class PeopleCoursesTable(Base):
    __tablename__ = "people_courses"
    
    id = Column(String, primary_key=True)
    person_id = Column(String, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    
    # Course information from crawler
    course_number = Column(String, nullable=True)    # From courses array
    course_name = Column(String, nullable=True)      # From courses array
    semester = Column(String, nullable=True)         # From courses array
    course_url = Column(String, nullable=True)       # From courses array
    
    person = relationship("PeopleTable", back_populates="courses")