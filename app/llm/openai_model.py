import openai 
from langchain.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI, OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader

from app.core.config import settings
import os

class OpenAIModel:
    def __init__(self):
        self.model_name = 'gpt-4o-mini-2024-07-18'
        self.embedding = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY,model='text-embedding-3-small')
        self.thresh = 0.5
        self.chat_bot = ChatOpenAI(model_name=self.model_name, openai_api_key=settings.OPENAI_API_KEY)
        self.client = OpenAI(openai_api_key=settings.OPENAI_API_KEY)

    def build_vector_db(self, chatbot_id: str, data_files: list[dict[str, str]]) -> None:
        documents = []

        for data_file in data_files:
            if data_file['type'] == 'csv':
                loader = CSVLoader(data_file['path'])
                documents.extend(loader.load())
            else:
                with open(data_file['path'], 'r', encoding='utf-8') as file:
                    text = file.read()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                texts = text_splitter.split_text(text)
                documents.extend([{"text": txt, "metadata": {"chatbot_id": chatbot_id}} for txt in texts])

        faiss = FAISS.from_texts([doc["text"] for doc in documents], embedding=self.embedding)

        directory = f"data/vector_dbs"
        if not os.path.exists(directory):
            os.makedirs(directory)
        faiss.save_local(f"{directory}/{chatbot_id}_faiss.index")
        return faiss

    def load_vector_db(self, chatbot_id: str):
        directory = f"data/vector_dbs"
        faiss = FAISS.load_local(f"{directory}/{chatbot_id}_faiss.index", 
                                 embeddings=self.embedding,
                                 allow_dangerous_deserialization=True)
        return faiss

    def delete_vector_db(self, chatbot_id: str):
        directory = f"data/vector_dbs"
        os.remove(f"{directory}/{chatbot_id}_faiss.index")

    def ask_by_chatbot_id(self, chatbot_id: str, question: str) -> dict:
        faiss = self.load_vector_db(chatbot_id)
        question_vector = self.embedding.embed_query(question)

        results = faiss.similarity_search_by_vector(question_vector, k=5)
        if results:
            top_result = results[0]

            return {"answer": top_result.page_content}

        response = self.client.Completion.create(
            model=self.model_name,
            prompt=question,
            max_tokens=150
        )
        return {"answer": response.choices[0].text.strip()}

    def ask_by_faiss(self, faiss: FAISS, question: str) -> dict:
        question_vector = self.embedding.embed_query(question)

        results = faiss.similarity_search_by_vector(question_vector, k=5)
        if results:
            top_result = results[0]

            return {"answer": top_result.page_content}

        response = self.client.Completion.create(
            model=self.model_name,
            prompt=question,
            max_tokens=150
        )
        return {"answer": response.choices[0].text.strip()}
    
openai_model = OpenAIModel()