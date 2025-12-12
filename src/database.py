"""
Database configuration and models for Slalom Capabilities Management System
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database URL - using SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./capabilities.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Association table for many-to-many relationship between capabilities and consultants
capability_consultants = Table(
    'capability_consultants',
    Base.metadata,
    Column('capability_id', Integer, ForeignKey('capabilities.id'), primary_key=True),
    Column('consultant_id', Integer, ForeignKey('consultants.id'), primary_key=True)
)


class Capability(Base):
    """Represents a consulting capability"""
    __tablename__ = "capabilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    practice_area = Column(String, nullable=False)
    skill_levels = Column(String, nullable=False)  # Stored as comma-separated
    certifications = Column(String, nullable=False)  # Stored as comma-separated
    industry_verticals = Column(String, nullable=False)  # Stored as comma-separated
    capacity = Column(Integer, nullable=False)

    # Relationship to consultants
    consultants = relationship(
        "Consultant",
        secondary=capability_consultants,
        back_populates="capabilities"
    )


class Consultant(Base):
    """Represents a consultant"""
    __tablename__ = "consultants"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # Relationship to capabilities
    capabilities = relationship(
        "Capability",
        secondary=capability_consultants,
        back_populates="consultants"
    )


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database with tables and seed data"""
    Base.metadata.create_all(bind=engine)

    # Seed initial data if database is empty
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Capability).count() == 0:
            # Initial capabilities data
            initial_capabilities = [
                {
                    "name": "Cloud Architecture",
                    "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
                    "practice_area": "Technology",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "AWS Solutions Architect,Azure Architect Expert",
                    "industry_verticals": "Healthcare,Financial Services,Retail",
                    "capacity": 40,
                    "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"]
                },
                {
                    "name": "Data Analytics",
                    "description": "Advanced data analysis, visualization, and machine learning solutions",
                    "practice_area": "Technology",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Tableau Desktop Specialist,Power BI Expert,Google Analytics",
                    "industry_verticals": "Retail,Healthcare,Manufacturing",
                    "capacity": 35,
                    "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"]
                },
                {
                    "name": "DevOps Engineering",
                    "description": "CI/CD pipeline design, infrastructure automation, and containerization",
                    "practice_area": "Technology",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Docker Certified Associate,Kubernetes Admin,Jenkins Certified",
                    "industry_verticals": "Technology,Financial Services",
                    "capacity": 30,
                    "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"]
                },
                {
                    "name": "Digital Strategy",
                    "description": "Digital transformation planning and strategic technology roadmaps",
                    "practice_area": "Strategy",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Digital Transformation Certificate,Agile Certified Practitioner",
                    "industry_verticals": "Healthcare,Financial Services,Government",
                    "capacity": 25,
                    "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"]
                },
                {
                    "name": "Change Management",
                    "description": "Organizational change leadership and adoption strategies",
                    "practice_area": "Operations",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Prosci Certified,Lean Six Sigma Black Belt",
                    "industry_verticals": "Healthcare,Manufacturing,Government",
                    "capacity": 20,
                    "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"]
                },
                {
                    "name": "UX/UI Design",
                    "description": "User experience design and digital product innovation",
                    "practice_area": "Technology",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Adobe Certified Expert,Google UX Design Certificate",
                    "industry_verticals": "Retail,Healthcare,Technology",
                    "capacity": 30,
                    "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"]
                },
                {
                    "name": "Cybersecurity",
                    "description": "Information security strategy, risk assessment, and compliance",
                    "practice_area": "Technology",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "CISSP,CISM,CompTIA Security+",
                    "industry_verticals": "Financial Services,Healthcare,Government",
                    "capacity": 25,
                    "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"]
                },
                {
                    "name": "Business Intelligence",
                    "description": "Enterprise reporting, data warehousing, and business analytics",
                    "practice_area": "Technology",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Microsoft BI Certification,Qlik Sense Certified",
                    "industry_verticals": "Retail,Manufacturing,Financial Services",
                    "capacity": 35,
                    "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"]
                },
                {
                    "name": "Agile Coaching",
                    "description": "Agile transformation and team coaching for scaled delivery",
                    "practice_area": "Operations",
                    "skill_levels": "Emerging,Proficient,Advanced,Expert",
                    "certifications": "Certified Scrum Master,SAFe Agilist,ICAgile Certified",
                    "industry_verticals": "Technology,Financial Services,Healthcare",
                    "capacity": 20,
                    "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"]
                }
            ]

            # Create capabilities and consultants
            for cap_data in initial_capabilities:
                # Extract consultant emails
                consultant_emails = cap_data.pop("consultants")

                # Create capability
                capability = Capability(**cap_data)
                db.add(capability)
                db.flush()  # Get the ID

                # Create or get consultants and associate them
                for email in consultant_emails:
                    consultant = db.query(Consultant).filter(Consultant.email == email).first()
                    if not consultant:
                        consultant = Consultant(email=email)
                        db.add(consultant)
                        db.flush()
                    capability.consultants.append(consultant)

            db.commit()
            print("Database initialized with seed data")
    finally:
        db.close()
