from pydantic import BaseModel
from typing import Optional

class ProjectOverviewCreate(BaseModel):
    business_description: str
    target_users: str
    main_features: str

class TechnologyStackCreate(BaseModel):
    frontend: str
    backend: str
    database: str
    infrastructure: str
    tools: str

class ProjectStructureCreate(BaseModel):
    folder_structure: str
    naming_conventions: str
    architecture_approach: str