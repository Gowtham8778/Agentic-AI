from pydantic import BaseModel, Field, ConfigDict
from typing import List
class Files (BaseModel) : 
    path:str = Field(description='the path to the file to be created or modified')
    purpose:str=Field(description="the purpose of the file e.g.'main application logic','data preprocessing module',etc. ")


class Plan(BaseModel) : 
    name : str = Field(description='the name of the app to build')
    description : str = Field(description = "a oneline description of the app to be build e.g. 'a web application for managing '")
    techstack:str=Field(description = "the tech stack to be used to build the app,e.g. 'python','java script','react','flask',etc.")
    features : list[str]=Field(description="the list of features that app should have e.g 'user authenticator','data visualization'")
    files : list[Files]=Field(description="a list of file to be created with 'path','purpose'")

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A detailed description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")