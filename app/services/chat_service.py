from typing import Optional
import uuid
import requests
from bs4 import BeautifulSoup

from app.llm.openai_model import openai_model
import requests
from bs4 import BeautifulSoup
from app.helper.json import load_json

class ChatService:
    def __init__(self):
        self.openai_model = openai_model

    def generate_warning(self) -> dict:
        url = "https://nchmf.gov.vn/Kttv/vi-VN/1/index.html"

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_container = soup.find("div", {"id": "left-col"})

            news_items = news_container.find_all("li")

            news_list = []

            for item in news_items:
                title = item.find("a").text.strip()

                link = item.find("a")["href"]

                time_label = item.find("label").text.strip() if item.find("label") else "Không rõ thời gian"


                news_list.append({
                    "title": title,
                    "link": link,
                    "time": time_label,
                })
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