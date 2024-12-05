from typing import Optional
import uuid

from app.llm.openai_model import openai_model
import requests
from bs4 import BeautifulSoup
from app.helper.json import load_json
from app.helper.crawl_nchmf import crawl_nchmf, crawl_all_news
from app.helper.crawl_vndms import get_vndms_warning_list
from datetime import datetime

class ChatService:
    def __init__(self):
        self.openai_model = openai_model

    def generate_warning(self) -> dict:
        news_list = crawl_nchmf()
        context = ""
        for news in news_list:
            context += f"Title: {news['title']}\nLink: {news['link']}\nTime: {news['time']}\n\n"
            
        prompt = f"""
            Please process the following data and return it as an array of JSON objects. Each object should include the following fields:
            title: The full title of the alert.
            date: The date extracted from the time field (format: YYYY-MM-DD).
            time: The time extracted from the time field (format: HH:mm:ss).
            link: The URL provided in the data.
            type: The main type of alert (e.g., lũ quét). If there are multiple types, create an array of types.
            region: The regions mentioned in the alert (e.g. Hà Tĩnh). If there are multiple regions, create an array of regions.
            Here is the data to process:
            {context}
            Respond strictly in JSON format. don't include any other information in the response like 'Here is the processed data as an array of JSON objects:'
        """
        answer = self.openai_model.ask_without_faiss(prompt)["answer"]
        return {
            "data": load_json(answer)
            }
        
    def create_chatbot(self) -> str:
        chatbot_id = datetime.now().strftime("%Y%m%d")
        if openai_model.is_id_exist(chatbot_id):
            raise Exception("Chatbot is already created")
        texts = crawl_all_news()
        vndms_data = get_vndms_warning_list()
        for data in vndms_data:
            if 'popupInfo' in data:
                del data['popupInfo']
            if 'source' in data:
                del data['source']
            if 'stationCode' in data:
                del data['stationCode']
            
        texts.extend([f"Dữ liệu cảnh báo thiên tai ngày {datetime.now().strftime('%d/%m/%Y')}: "+str(data) for data in vndms_data])
        openai_model.build_vector_db_by_text(chatbot_id, texts)
        
        return {
            "message": "Chatbot is created successfully"
        }
        
    def ask_latest_chatbot(self, question: str) -> str:
        latest_chatbot_id = openai_model.latest_chatbot_id()
        response = openai_model.ask_by_chatbot_id(latest_chatbot_id, question)
        return response