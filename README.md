# Emergix LCDP Backend Services

# Getting Started

## Clone the repository

```
git clone https://github.com/vku-open-source/llm-service.git
```
## cd into project root

```
cd llm-service
```

## Launch app

#### 1. Prepare environment
- Create `.env` file in the root directory.
- Copy content from `.env.example` and change to your correct data.

#### 2. Start app
#### 2.1. Run locally
```
uv sync
source .venv/bin/activate
fastapi dev app/main.py
```

#### 2.2. Using Docker
```
docker compose up -d
```
Afterwards, FastAPI automatically generates documentation based on the specification of the endpoints you have written. You can find the docs at http://localhost:8000/docs.

#### 3. API list

#### 1. API to generate warnings
- Crawl warnings data from nchmf and process with LLM: [POST]: `/api/v1/chat/generate-warnings`

| Params | Description            | Default |
| ------ | ---------------------- | ------- |
| N/A    | No required parameters | N/A     |


This API is intended to support generating warning data for the LCDP Backend. The LCDP Backend runs a cron job every day at 0:00 to call this API to get daily warning data.

#### 2. API to generate chatbot by yesterday data
- Crawl data from nchmf and vndms and load into vectorstore: [POST]: `/api/v1/chat/create-chatbot`

| Params | Description            | Default |
| ------ | ---------------------- | ------- |
| N/A    | No required parameters | N/A     |

This API aims to crawl data from NCHMF and VNDMS to create a vectorstore to help create the latest information warehouse to feed our AI chatbot. The LCDP Backend runs a cron job every day at 0:00 to call this API to generate new chatbot vectorstore.

#### 2. API to ask the latest chatbot
- Respond with relevant warning information or other data based on the input question: [POST]: `/api/v1/chat/ask-latest-chatbot`

| Params | Description            | Default |
| ------ | ---------------------- | ------- |
| question    | The prompt to ask | N/A     |

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the terms of the [Apache V2.0](LICENSE)