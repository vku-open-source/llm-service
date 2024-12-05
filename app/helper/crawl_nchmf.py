from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

from .pdf import extract_text_from_pdf

def crawl_nchmf():
    url = "https://nchmf.gov.vn/Kttv/vi-VN/1/index.html"

    news_list = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        news_container = soup.find("div", {"id": "left-col"})

        news_items = news_container.find_all("li")


        for item in news_items:
            title = item.find("a").text.strip()

            link = item.find("a")["href"]

            time_label = item.find("label").text.strip() if item.find("label") else "Không rõ thời gian"


            news_list.append({
                "title": title,
                "link": link,
                "time": time_label,
            })
            
    return news_list


def extract_text_recursively(element):
    """Hàm đệ quy để trích xuất văn bản từ một phần tử HTML, tránh các thẻ <script>."""
    text = ""
    for child in element.children:
        if child.name:  # Nếu là thẻ HTML
            if child.name == 'script':  # Bỏ qua thẻ <script>
                continue
            text += extract_text_recursively(child)
        elif isinstance(child, str):  # Nếu là chuỗi văn bản
            text += child.strip() + "\n"
    return text.strip()

def extract_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page, status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))

    if len(pdf_links) > 0:
        os.makedirs("temp_pdfs", exist_ok=True)

        for link in pdf_links:
            pdf_url = link['href']
            if not pdf_url.startswith("http"):  # Nếu là đường dẫn tương đối
                pdf_url = requests.compat.urljoin(url, pdf_url)

            print(f"Fetching PDF: {pdf_url}")
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                file_name = os.path.join("temp_pdfs", os.path.basename(pdf_url))
                with open(file_name, "wb") as pdf_file:
                    pdf_file.write(pdf_response.content)
                print(f"Saved PDF: {file_name}")

                text = extract_text_from_pdf(file_name)
                os.remove(file_name)
                return text
            else:
                print(f"Failed to download PDF: {pdf_url}")
    else:
        print("No PDFs found. Extracting text from HTML content.")
        content_news = soup.find(class_='content-news')
        if content_news:
            text = extract_text_recursively(content_news)
            print("Extracted Text:\n")
            print(text)
            return text
        else:
            print("No element with class 'content-news' found.")
            
    return text

def crawl_all_news():
    news_list = crawl_nchmf()
    texts = [f"Hôm nay là ngày {datetime.now().strftime('%d/%m/%Y')}\n\n"]
    for news in news_list:
        texts.append(extract_from_url(news['link']))
    
    return texts
        