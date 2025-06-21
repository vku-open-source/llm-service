# Emergency Operations Plan (EOP) Generation

## Overview

The EOP Generation feature uses LangChain workflow to automatically create comprehensive Emergency Operations Plans for flood scenarios. The system analyzes flood data, available resources, and location information to generate actionable emergency response plans in Vietnamese.

## API Endpoints

### 1. POST `/api/ai/generate-eop`

Generates an Emergency Operations Plan based on provided flood and resource data.

#### Request Body

```json
{
  "flood_data": "string",
  "resource_data": "string",
  "location": "string"
}
```

#### Parameters

- `flood_data` (required): Information about the flood situation including water levels, affected areas, and projections
- `resource_data` (required): Information about available resources such as rescue boats, medical supplies, volunteers, etc.
- `location` (required): Location information for the emergency response

#### Response

```json
{
  "status": "success",
  "eop_report": "Generated EOP content in Vietnamese",
  "metadata": {
    "location": "string",
    "generated_at": "ISO timestamp",
    "model_used": "gpt-4o-mini-2024-07-18"
  }
}
```

### 2. POST `/api/ai/generate-tasks`

Generates volunteer tasks based on an Emergency Operations Plan (EOP) and current situation data.

#### Request Body

```json
{
  "emergency_operations_plan": "string",
  "flood_data": "string",
  "resource_data": "string"
}
```

#### Parameters

- `emergency_operations_plan` (required): The EOP report content (can be edited by user)
- `flood_data` (required): Current flood situation data
- `resource_data` (required): Available resources information

#### Response

```json
{
  "status": "success",
  "tasks": [
    {
      "priority": "High/Medium/Low",
      "description": "Clear, concise task description",
      "location": "General location or area for the task",
      "resource_needed": "List of resources required, if any"
    }
  ],
  "total_tasks": 8,
  "metadata": {
    "generated_at": "ISO timestamp",
    "model_used": "gpt-4o-mini-2024-07-18"
  }
}
```

## Example Usage

### EOP Generation Example

```bash
curl -X POST "http://localhost:8000/api/ai/generate-eop" \
  -H "Content-Type: application/json" \
  -d '{
    "flood_data": "Mực nước sông Hồng đang dâng cao, hiện tại ở mức 12.5m, dự báo sẽ lên 13.2m trong 24h tới. Khu vực ven sông đã bị ngập lụt.",
    "resource_data": "Có 50 thuyền cứu hộ, 200 bao cát, 1000 suất ăn khẩn cấp, 50 nhân viên y tế, 200 tình nguyện viên.",
    "location": "Hà Nội - Khu vực ven sông Hồng"
  }'
```

### Task Generation Example

```bash
curl -X POST "http://localhost:8000/api/ai/generate-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "emergency_operations_plan": "<EOP>\n# Tổng quan tình hình\nMực nước sông Hồng đang ở mức 12.5m và dự báo sẽ lên 13.2m trong 24h tới.\n\n# Sứ mệnh và mục tiêu\nĐảm bảo an toàn cho người dân trong khu vực bị ảnh hưởng.\n\n# Phân bổ nguồn lực\n- 50 thuyền cứu hộ: Phân bổ cho các khu vực ngập lụt.\n- 200 bao cát: Tập trung tại các điểm yếu.\n\n# Kế hoạch truyền thông\nThiết lập hệ thống cảnh báo qua loa phát thanh.\n</EOP>",
    "flood_data": "Mực nước sông Hồng đang dâng cao, hiện tại ở mức 12.5m, dự báo sẽ lên 13.2m trong 24h tới. Khu vực ven sông đã bị ngập lụt.",
    "resource_data": "Có 50 thuyền cứu hộ, 200 bao cát, 1000 suất ăn khẩn cấp, 50 nhân viên y tế, 200 tình nguyện viên."
  }'
```

## EOP Structure

The generated EOP includes the following sections:

1. **Tổng quan tình hình** (Situation Overview): Summary of current flood situation and potential risks
2. **Sứ mệnh và mục tiêu** (Mission and Objectives): Primary goals of the emergency response
3. **Phân bổ nguồn lực** (Resource Allocation): How available resources should be distributed and utilized
4. **Kế hoạch truyền thông** (Communication Plans): Communication strategies and protocols

## Task Structure

The generated tasks include the following fields:

1. **priority**: High/Medium/Low - Priority level of the task
2. **description**: Clear, concise task description in Vietnamese
3. **location**: General location or area where the task should be performed
4. **resource_needed**: List of resources required to complete the task

## Workflow

1. **Generate EOP**: Use `/api/ai/generate-eop` to create initial Emergency Operations Plan
2. **Edit EOP**: User can modify the generated EOP report as needed
3. **Generate Tasks**: Use `/api/ai/generate-tasks` with the edited EOP to create volunteer tasks
4. **Deploy Tasks**: Assign generated tasks to volunteers for execution

## Error Handling

The API returns appropriate HTTP status codes:

- `400 Bad Request`: Missing required fields
- `500 Internal Server Error`: Server-side errors during generation

## Technical Implementation

### LangChain Workflows

Both endpoints use LangChain's `LLMChain` with custom prompt templates:

1. **EOP Generation**: Analyzes flood data, resources, and location to create comprehensive emergency plans
2. **Task Generation**: Analyzes EOP, current situation, and resources to create prioritized volunteer tasks

### Dependencies

- `langchain`: Core workflow framework
- `langchain-openai`: OpenAI integration
- `fastapi`: API framework
- `pydantic`: Data validation

### Files

- `app/services/eop_service.py`: Core EOP generation service
- `app/services/task_service.py`: Core task generation service
- `app/api/routes/ai.py`: API endpoint implementations
- `app/api/routes/request_models/chat_request.py`: Request/response models
- `app/tests/api/routes/test_eop_generation.py`: EOP generation tests
- `app/tests/api/routes/test_task_generation.py`: Task generation tests

## Testing

Run the tests using:

```bash
# Test EOP generation
pytest app/tests/api/routes/test_eop_generation.py -v

# Test task generation
pytest app/tests/api/routes/test_task_generation.py -v
```

## Configuration

The services use the following configuration from `app/core/config.py`:

- `OPENAI_API_KEY`: OpenAI API key for LLM access
- Model: `gpt-4o-mini-2024-07-18`
- Temperature: 0.7 (for balanced creativity and consistency)