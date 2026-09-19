from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    repo: str
    environment: str
    owner: str
    awsEnvironment: str

class ProjectResponse(ProjectCreate):
    projectId: str
    createdAt: datetime
    updatedAt: datetime
