### Requirements

- Docker.
- uv for Python package and environment management.

### How to run

- docker compose -f docker-compose-dev.yml watch
- uv sync
- cp .env.example .env
- Change .env environment(openai api key)
- source .venv/bin/activate
- alembic upgrade head
- fastapi dev app/main.py

### How to commit a migration

- alembic revision --autogenerate -m "Commit message"

## Chatbot API documentation

# Chatbot Management:

- POST /api/v1/chatbots/: Tạo chatbot mới
- GET /api/v1/chatbots/: Lấy danh sách chatbot của user
- GET /api/v1/chatbots/{chatbot_id}: Lấy thông tin chatbot
- PUT /api/v1/chatbots/{chatbot_id}: Cập nhật chatbot
- DELETE /api/v1/chatbots/{chatbot_id}: Xóa chatbot

# Training:

- POST /api/v1/chatbots/{chatbot_id}/train: Train chatbot với files

# Chat (existing):

- POST /api/v1/chat/: Chat với chatbot
  Tất cả các endpoints đều yêu cầu authentication và kiểm tra quyền sở hữu của chatbot. Khi xóa một chatbot, hệ thống sẽ xóa cả vector database của chatbot đó.

# Chat API documentation

- API sẽ có các endpoint sau:
  - POST /api/v1/chat: Gửi tin nhắn và nhận phản hồi
  - POST /api/v1/train: Train chatbot với dữ liệu mới
  - DELETE /api/v1/chatbot/{chatbot_id}: Xóa dữ liệu của một chatbot
- Bạn có thể test API bằng cách gửi request:
  - POST http://localhost:8000/api/v1/chat
  - POST http://localhost:8000/api/v1/train
  - DELETE http://localhost:8000/api/v1/chatbot/{chatbot_id}
- Lưu ý:
  - Chatbot_id là tên của chatbot mà bạn muốn gửi tin nhắn.
  - Bạn có thể lấy chatbot_id bằng cách GET http://localhost:8000/api/v1/chatbot
  - Session_id là id của phiên trò chuyện, nó sẽ được trả về khi gửi request POST /api/v1/chat
