import re
from app.helper.pdf import extract_text_from_pdf
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
        
    def is_id_exist(self, chatbot_id: str) -> bool:
        directory = f"data/vector_dbs"
        return os.path.exists(f"{directory}/{chatbot_id}_faiss.index")
    
    def latest_chatbot_id(self) -> str:
        directory = "data/vector_dbs"
        files = os.listdir(directory)
        if files:
            files.sort() 
            return files[-1].split("_")[0]
        return None

    def build_vector_db(self, chatbot_id: str, data_files: list[dict[str, str]]) -> None:
        documents = []

        for data_file in data_files:
            if data_file['type'] == 'csv':
                loader = CSVLoader(data_file['path'])
                documents.extend(loader.load())
            elif data_file['type'] == 'pdf':
                text = extract_text_from_pdf(data_file['path'])
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
                texts = text_splitter.split_text(text)
                documents.extend([{"text": txt, "metadata": {"chatbot_id": chatbot_id}} for txt in texts])
            else:
                with open(data_file['path'], 'r', encoding='utf-8') as file:
                    text = file.read()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
                texts = text_splitter.split_text(text)
                documents.extend([{"text": txt, "metadata": {"chatbot_id": chatbot_id}} for txt in texts])

        faiss = FAISS.from_texts([doc["text"] for doc in documents], embedding=self.embedding)

        directory = f"data/vector_dbs"
        faiss.save_local(f"{directory}/{chatbot_id}_faiss.index")
        return faiss
    
    def build_vector_db_by_text(self, chatbot_id: str, texts: list[str]) -> None:
        documents = []

        for text in texts:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
            texts = text_splitter.split_text(text)
            documents.extend([{"text": txt, "metadata": {"chatbot_id": chatbot_id}} for txt in texts])

        faiss = FAISS.from_texts([doc["text"] for doc in documents], embedding=self.embedding)

        directory = f"data/vector_dbs"
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

    def ask_by_faiss(self, faiss: FAISS, question: str) -> dict:
        question_vector = self.embedding.embed_query(question)

        results = faiss.similarity_search_by_vector(question_vector, k=10)
        if results:
            top_contexts = [result.page_content.strip() for result in results]
            context = "\n".join(top_contexts)
            print(context)

            prompt = (
                f"Context:\n{context}\n\n"
                f"Question: {question}\n"
                f"Answer:"
            )
            response = self.chat_bot(messages=prompt).content
            raw_answer = response
            clean_answer = re.sub(r'\s+', ' ', raw_answer)
            return {"answer": clean_answer}

        response = self.chat_bot(messages=question).content
        
        raw_answer = response
        clean_answer = re.sub(r'\s+', ' ', raw_answer)
        return {"answer": clean_answer}

    def ask_by_chatbot_id(self, chatbot_id: str, question: str) -> dict:
        faiss = self.load_vector_db(chatbot_id)
        return self.ask_by_faiss(faiss, question)


    
    def ask_without_faiss(self, question: str) -> dict:
        messages = [{"role": "user", "content": question}]
        response = self.chat_bot(messages=messages)
        return {"answer": response.content}
    
openai_model = OpenAIModel()
