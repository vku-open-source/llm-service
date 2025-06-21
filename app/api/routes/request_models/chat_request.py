from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

class EOPGenerationRequest(BaseModel):
    flood_data: str
    resource_data: str
    location: str

class TaskGenerationRequest(BaseModel):
    emergency_operations_plan: str
    flood_data: str
    resource_data: str