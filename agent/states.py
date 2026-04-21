from pydantic import BaseModel, Field
from typing import List, Optional


class Files(BaseModel):
    path: str = Field(description="Path to the file")
    purpose: str = Field(description="Purpose of the file")


class Plan(BaseModel):
    name: str = Field(description="Name of the application")
    description: str = Field(description="Short description of the app")
    techstack: str = Field(description="Tech stack to be used")
    features: List[str] = Field(description="List of features")
    files: List[Files] = Field(description="List of files with purpose")


class ImplementationTask(BaseModel):
    filepath: str = Field(description="File path")
    task_description: str = Field(description="Detailed task description")


class TaskPlan(BaseModel):
    name: str = Field(description="Project name")
    description: str = Field(description="Project description")
    implementation_steps: List[ImplementationTask] = Field(
        description="Steps to implement the project"
    )


class CoderState(BaseModel):
    task_plan: TaskPlan
    current_step_idx: int = 0
    current_file_content: Optional[str] = Noneclass Plan(BaseModel):
    name: str
    description: str
    techstack: str
    features: List[str]
    files: List[Files]