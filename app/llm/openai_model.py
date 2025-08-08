import os
import re
import os

from app.helper.pdf import extract_text_from_pdf
from langchain.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings, OpenAI
from app.core.config import settings


class OpenAIModel:
    def __init__(self):
        self.model_name = "gpt-4o"
        self.embedding = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-3-small"
        )
        self.thresh = 0.5
        # Threshold for relevant content (lower score = higher similarity)
        self.similarity_threshold = 0.2
        self.chat_bot = ChatOpenAI(
            model_name=self.model_name, openai_api_key=settings.OPENAI_API_KEY
        )
        self.client = OpenAI(openai_api_key=settings.OPENAI_API_KEY)

    def is_id_exist(self, chatbot_id: str) -> bool:
        directory = "data/vector_dbs"
        return os.path.exists(f"{directory}/{chatbot_id}_faiss.index")

    def latest_chatbot_id(self) -> str:
        directory = "data/vector_dbs"
        files = os.listdir(directory)
        if files:
            files.sort()
            return files[-1].split("_")[0]
        return None

    def build_vector_db(
        self, chatbot_id: str, data_files: list[dict[str, str]]
    ) -> None:
        documents = []

        for data_file in data_files:
            if data_file["type"] == "csv":
                loader = CSVLoader(data_file["path"])
                documents.extend(loader.load())
            elif data_file["type"] == "pdf":
                text = extract_text_from_pdf(data_file["path"])
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, chunk_overlap=500
                )
                texts = text_splitter.split_text(text)
                documents.extend(
                    [
                        {"text": txt, "metadata": {"chatbot_id": chatbot_id}}
                        for txt in texts
                    ]
                )
            else:
                with open(data_file["path"], "r", encoding="utf-8") as file:
                    text = file.read()
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, chunk_overlap=500
                )
                texts = text_splitter.split_text(text)
                documents.extend(
                    [
                        {"text": txt, "metadata": {"chatbot_id": chatbot_id}}
                        for txt in texts
                    ]
                )

        faiss = FAISS.from_texts(
            [doc["text"] for doc in documents], embedding=self.embedding
        )

        directory = "data/vector_dbs"
        os.makedirs(directory, exist_ok=True)
        faiss.save_local(f"{directory}/{chatbot_id}_faiss.index")
        return faiss

    def build_vector_db_by_text(self, chatbot_id: str, texts: list[str]) -> None:
        documents = []

        for text in texts:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=500
            )
            texts = text_splitter.split_text(text)
            documents.extend(
                [{"text": txt, "metadata": {"chatbot_id": chatbot_id}} for txt in texts]
            )

        faiss = FAISS.from_texts(
            [doc["text"] for doc in documents], embedding=self.embedding
        )

        directory = "data/vector_dbs"
        os.makedirs(directory, exist_ok=True)
        faiss.save_local(f"{directory}/{chatbot_id}_faiss.index")
        return faiss

    def load_vector_db(self, chatbot_id: str):
        directory = "data/vector_dbs"
        faiss = FAISS.load_local(
            f"{directory}/{chatbot_id}_faiss.index",
            embeddings=self.embedding,
            allow_dangerous_deserialization=True,
        )
        return faiss

    def delete_vector_db(self, chatbot_id: str):
        directory = "data/vector_dbs"
        os.remove(f"{directory}/{chatbot_id}_faiss.index")

    def ask_by_faiss(
        self, faiss: FAISS, question: str, similarity_threshold: float = None
    ) -> dict:
        try:
            # Use provided threshold or default
            # threshold = (
            #     similarity_threshold
            #     if similarity_threshold is not None
            #     else self.similarity_threshold
            # )

            question_vector = self.embedding.embed_query(question)

            # Get similarity search results with scores
            results = faiss.similarity_search_by_vector(question_vector, k=20)
            print("results", results)

            if results:
                # Filter by similarity threshold (lower = higher similarity)
                # filtered_results = [
                #     (result, score) for result, score in results if score < threshold
                # ]
                filtered_results = results

                # Sort by similarity score (ascending, so most similar first)
                # filtered_results = sorted(filtered_results, key=lambda x: x[1])

                if filtered_results:
                    top_contexts = [
                        result.page_content.strip() for result in filtered_results
                    ]
                    context = "\n".join(top_contexts)
                    print(f"Found {len(filtered_results)} relevant contexts")

                    disaster_expert_prompt = (
                        "Bạn là một chuyên gia tư vấn thông tin thiên tai và "
                        "khẩn cấp của Việt Nam. Nhiệm vụ của bạn là cung cấp "
                        "thông tin chính xác, kịp thời về thiên tai, "
                        "cảnh báo khí tượng, và hướng dẫn ứng phó khẩn cấp.\n\n"
                        "NGUYÊN TẮC HOẠT ĐỘNG:\n"
                        "1. Chỉ trả lời các câu hỏi liên quan đến thiên tai, "
                        "khí tượng, cảnh báo tự nhiên, và ứng phó khẩn cấp\n"
                        "2. Sử dụng CHÍNH XÁC thông tin từ dữ liệu được cung cấp\n"
                        "3. Nếu dữ liệu không đủ để trả lời câu hỏi, nói rõ "
                        "'Tôi không có đủ dữ liệu để trả lời câu hỏi này'\n"
                        "4. Trả lời bằng tiếng Việt, rõ ràng và dễ hiểu\n"
                        "5. Ưu tiên thông tin an toàn và cảnh báo kịp thời\n"
                        "6. ĐẶC BIỆT: Nếu có câu hỏi về 'nơi trú ẩn', 'chỗ ẩn náu', "
                        "'tôi nên trốn ở đâu', 'nên đi đâu để an toàn' hoặc tương tự, "
                        "hãy trả lời: 'Vui lòng liên hệ với cán bộ, lực lượng "
                        "chức năng gần nhất để được hướng dẫn về địa điểm trú ẩn "
                        "an toàn phù hợp với tình hình thực tế tại khu vực của bạn.'\n\n"
                        f"DỮ LIỆU THAM KHẢO:\n{context}\n\n"
                        f"CÂU HỎI: {question}\n\n"
                        "Hãy phân tích dữ liệu tham khảo và trả lời câu hỏi. "
                        "Nếu dữ liệu không chứa thông tin cần thiết để trả lời "
                        "chính xác câu hỏi, hãy trả lời: 'Tôi không có đủ dữ liệu "
                        "để trả lời câu hỏi này.'\n\nTRẢ LỜI:"
                    )

                    response = self.chat_bot(messages=disaster_expert_prompt).content
                    raw_answer = response
                    clean_answer = re.sub(r"\s+", " ", raw_answer)
                    print("clean_answer", clean_answer)

                    # Validate response - check if model says no enough data
                    insufficient_data_phrases = [
                        "không có đủ dữ liệu",
                        "không đủ thông tin",
                        "không tìm thấy thông tin",
                        "dữ liệu không đủ",
                    ]

                    if any(
                        phrase in clean_answer.lower()
                        for phrase in insufficient_data_phrases
                    ):
                        return {"answer": "Tôi không có đủ dữ liệu để trả lời câu hỏi này."}

                    return {"answer": clean_answer}
                else:
                    print("No relevant contexts found based on threshold")
                    return {"answer": "Tôi không có đủ dữ liệu để trả lời câu hỏi này."}

            # Fallback: if no FAISS results, ask general question with context
            fallback_prompt = (
                "Bạn là một chuyên gia tư vấn thông tin thiên tai và "
                "khẩn cấp của Việt Nam.\n\n"
                f"CÂU HỎI: {question}\n\n"
                "Nếu câu hỏi KHÔNG liên quan đến thiên tai, khí tượng, "
                "cảnh báo tự nhiên, hoặc ứng phó khẩn cấp, hãy trả lời: "
                "'Tôi chỉ có thể tư vấn về các vấn đề liên quan đến thiên tai "
                "và ứng phó khẩn cấp.'\n\n"
                "ĐẶC BIỆT: Nếu có câu hỏi về 'nơi trú ẩn', 'chỗ ẩn náu', "
                "'tôi nên trốn ở đâu', 'nên đi đâu để an toàn' hoặc tương tự, "
                "hãy trả lời: 'Vui lòng liên hệ với cán bộ, lực lượng "
                "chức năng gần nhất để được hướng dẫn về địa điểm trú ẩn "
                "an toàn phù hợp với tình hình thực tế tại khu vực của bạn.'\n\n"
                "Nếu câu hỏi có liên quan nhưng bạn không có thông tin cụ thể, "
                "hãy trả lời: 'Tôi không có đủ dữ liệu để trả lời câu hỏi này.'"
                "\n\nTRẢ LỜI:"
            )

            response = self.chat_bot(messages=fallback_prompt).content
            raw_answer = response
            clean_answer = re.sub(r"\s+", " ", raw_answer)
            return {"answer": clean_answer}
        except Exception as e:
            print('error ask by faiss', str(e))
            raise e

    def ask_by_chatbot_id(
        self, chatbot_id: str, question: str, similarity_threshold: float = None
    ) -> dict:
        faiss = self.load_vector_db(chatbot_id)
        return self.ask_by_faiss(faiss, question, similarity_threshold)

    def ask_without_faiss(self, question: str) -> dict:
        # Apply disaster context even without FAISS
        disaster_prompt = (
            "Bạn là một chuyên gia tư vấn thông tin thiên tai và "
            "khẩn cấp của Việt Nam.\n\n"
            f"CÂU HỎI: {question}\n\n"
            "Nếu câu hỏi KHÔNG liên quan đến thiên tai, khí tượng, "
            "cảnh báo tự nhiên, hoặc ứng phó khẩn cấp, hãy trả lời: "
            "'Tôi chỉ có thể tư vấn về các vấn đề liên quan đến thiên tai "
            "và ứng phó khẩn cấp.'\n\n"
            "ĐẶC BIỆT: Nếu có câu hỏi về 'nơi trú ẩn', 'chỗ ẩn náu', "
            "'tôi nên trốn ở đâu', 'nên đi đâu để an toàn' hoặc tương tự, "
            "hãy trả lời: 'Vui lòng liên hệ với cán bộ, lực lượng "
            "chức năng gần nhất để được hướng dẫn về địa điểm trú ẩn "
            "an toàn phù hợp với tình hình thực tế tại khu vực của bạn.'\n\n"
            "Nếu câu hỏi có liên quan nhưng bạn không có thông tin cụ thể "
            "từ cơ sở dữ liệu, hãy trả lời: 'Tôi không có đủ dữ liệu để "
            "trả lời câu hỏi này.'\n\nTRẢ LỜI:"
        )

        messages = [{"role": "user", "content": disaster_prompt}]
        response = self.chat_bot(messages=messages)
        return {"answer": response.content}


openai_model = OpenAIModel()
