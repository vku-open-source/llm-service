from fastapi import APIRouter, HTTPException
from app.api.routes.request_models.chat_request import EOPGenerationRequest, TaskGenerationRequest
from app.services.eop_service import eop_service
from app.services.task_service import task_service
from typing import Dict, Any

router = APIRouter()

@router.post("/generate-eop", response_model=Dict[str, Any])
async def generate_eop(request: EOPGenerationRequest) -> Dict[str, Any]:
    """
    Generate an Emergency Operations Plan (EOP) based on flood and resource data.

    This endpoint uses LangChain workflow to analyze flood data, resource availability,
    and location information to create a comprehensive emergency response plan.

    Args:
        request: EOPGenerationRequest containing flood_data, resource_data, and location

    Returns:
        Dictionary containing the generated EOP report with status and metadata
    """
    try:
        # Validate input data
        if not request.flood_data.strip():
            raise HTTPException(status_code=400, detail="Flood data is required")

        if not request.resource_data.strip():
            raise HTTPException(status_code=400, detail="Resource data is required")

        if not request.location.strip():
            raise HTTPException(status_code=400, detail="Location is required")

        # Generate EOP using the service
        result = await eop_service.generate_eop(
            flood_data=request.flood_data,
            resource_data=request.resource_data,
            location=request.location
        )

        # Check if generation was successful
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate-tasks", response_model=Dict[str, Any])
async def generate_tasks(request: TaskGenerationRequest) -> Dict[str, Any]:
    """
    Generate volunteer tasks based on an Emergency Operations Plan (EOP) and current situation data.

    This endpoint uses LangChain workflow to analyze the EOP report, current flood data,
    and available resources to create a prioritized list of tasks for volunteers.

    Args:
        request: TaskGenerationRequest containing emergency_operations_plan, flood_data, and resource_data

    Returns:
        Dictionary containing the generated task list with priority, description, location, and resource_needed
    """
    try:
        # Validate input data
        if not request.emergency_operations_plan.strip():
            raise HTTPException(status_code=400, detail="Emergency operations plan is required")

        if not request.flood_data.strip():
            raise HTTPException(status_code=400, detail="Flood data is required")

        if not request.resource_data.strip():
            raise HTTPException(status_code=400, detail="Resource data is required")

        # Generate tasks using the service
        result = await task_service.generate_tasks(
            emergency_operations_plan=request.emergency_operations_plan,
            flood_data=request.flood_data,
            resource_data=request.resource_data
        )

        # Check if generation was successful
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")