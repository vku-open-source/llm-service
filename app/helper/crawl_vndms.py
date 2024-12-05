import requests
import re

from app.core.config import settings

def get_vndms_warning_list():
    try:
        # Gửi request tới API
        url = f"{settings.STRAPI_URL}/api/vndms-warnings?sort=datetime:desc&pagination[limit]=24"
        print(url)
        response = requests.get(url)
        # response.raise_for_status()  # Kiểm tra lỗi HTTP

        data = response.json().get('data', [])
        # Regex patterns
        source_regex = re.compile(r"detailrain\(`\d+`,`(.*?)`,\d+\)")
        site_regex = re.compile(r"Mã trạm:\s*<b>(.*?)<\/b>")

        seen_labels = set()  # Sử dụng set để lưu các label đã thấy

        # Flatten và lọc các object
        unique_data = []
        for item in data:
            for sub_item in item.get('data', []):
                popup_info = sub_item.get('popupInfo', '')

                # Trích xuất thông tin từ popupInfo
                source_match = source_regex.search(popup_info)
                site_match = site_regex.search(popup_info)

                sub_item['source'] = source_match.group(1) if source_match else None
                sub_item['stationCode'] = site_match.group(1) if site_match else None

                label = sub_item.get('label')
                if label and label not in seen_labels:
                    seen_labels.add(label)
                    unique_data.append(sub_item)

        return unique_data
    except Exception as e:
        print(e)
        return []
