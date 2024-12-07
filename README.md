# 🚀 Emergix - Unified Emergency Operations and Planning Platform Backend Services

Welcome to Emergix, the backend service platform for emergency operations and planning. Below is a guide on requirements, installation, and the main APIs of the project.

## I. Requirements

- [Node.js](https://nodejs.org/) (>= 18.0.0)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- [PostgreSQL](https://www.postgresql.org/download/) (for database)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## II. Installation and Running Applications

### 1. Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/vku-open-source/lcdp-backend.git
   cd lcdp-backend
   ```

2. Install dependencies:

   ```bash
   npm install
   # or
   yarn install
   ```

3. Set up environment variables:

   - Copy the `.env.example` file to `.env` and edit the values as needed.

4. Start the application:

   ```bash
   npm run develop
   # or
   yarn develop
   ```

### 2. Running in Docker

To run the application using Docker, you can use the provided `docker-compose.yml` file:

```bash
docker-compose up
```

## III. API Documentation

### Warning Module

#### 1. Provincial Warning 

- **Endpoint**: `GET /api/nchmf-warnings`
- **Description**: Retrieve warning information from the National Center for Hydro-Meteorological Forecasting.
- **Response**:

```json
{
  "data": [
    {
      "id": 2,
      "documentId": "oth0x2s3esof1bnnod79s9io",
      "date": "2024-11-30",
      "data": {
        "data": [
          {
            "date": "2024-11-30",
            "link": "https://nchmf.gov.vn/Kttv/vi-VN/1/tin-du-bao-gio-manh-song-lon-va-mua-dong-tren-bien-post1287.html",
            "time": "16:01:00",
            "type": ["dự báo"],
            "title": "TIN DỰ BÁO GIÓ MẠNH, SÓNG LỚN VÀ MƯA DÔNG TRÊN BIỂN",
            "region": []
          },
          {
            "date": "2024-11-28",
            "link": "https://nchmf.gov.vn/Kttv/vi-VN/1/tin-canh-bao-lu-quet-sat-lo-dat-sut-lun-dat-do-mua-lu-hoac-dong-chay-tren-khu-vuc-cac-tinh-ha-tinh-khanh-hoa-va-tu-thua-thien-hue-den-quang-ngai-post1321.html",
            "time": "13:30:49",
            "type": ["cảnh báo", "lũ quét", "sạt lở đất", "sụt lún đất"],
            "title": "TIN CẢNH BÁO LŨ QUÉT, SẠT LỞ ĐẤT, SỤT LÚN ĐẤT DO MƯA LŨ HOẶC DÒNG CHẢY TRÊN KHU VỰC CÁC TỈNH HÀ TĨNH, KHÁNH HÒA VÀ TỪ THỪA THIÊN HUẾ ĐẾN QUẢNG NGÃI",
            "region": ["Hà Tĩnh", "Khánh Hòa", "Thừa Thiên Huế", "Quảng Ngãi"]
          }
        ]
      }
    }
  ]
}
```

| Params | Description            | Default |
| ------ | ---------------------- | ------- |
| N/A    | No required parameters | N/A     |

#### 2. Warning by Coordinates 

- **Endpoint**: `GET /api/warning`
- **Description**: Retrieve warning information by coordinates from the Vietnam Disaster Monitoring System
- **Response**:

```json
{
  "data": [
    {
      "lat": 12.991999626159668,
      "long": 107.69200134277344,
      "label": "Đắk Nông",
      "warning_level": 1,
      "warning_type": "water_level",
      "water_level": "589.34"
    },
    {
      "lat": 20.933000564575195,
      "long": 106.76699829101562,
      "label": "Đồ Nghi",
      "warning_level": 1,
      "warning_type": "water_level",
      "water_level": "2"
    }
  ]
}
```

| Params | Description            | Default |
| ------ | ---------------------- | ------- |
| N/A    | No required parameters | N/A     |

### Resource Module

#### 1. Create EOP

- **Endpoint**: `POST /eop/generate-eop`
- **Description**: Create EOP based on input data (flood, resources).
- **Body**:

```json
{
  "floodData": "",
  "resourceData": ""
}
```

| Body         | Description   | Required |
| ------------ | ------------- | -------- |
| floodData    | Flood data    | true     |
| resourceData | Resource data | true     |

#### 2. Confirmed EOP

- **Endpoint**: `POST /eop/confirm-eop`
- **Description**: Users edit and confirm the new EOP, then create a task list.
- **Body**:

```json
{
  "eopId": "fume1l0bgng65vori8mff6s8",
  "content": ""
}
```

| Body    | Description    | Required |
| ------- | -------------- | -------- |
| eopId   | EOP ID         | true     |
| content | Edited content | true     |

### Community API

#### 1. Get Emergency Alerts

- **Endpoint**: `GET /api/communities?filters[type][$eq]=emergency_alert`
- **Description**: Retrieve a list of emergency alerts from the community.

```json
{
`  "data": [
    {
      "id": "1",
      "title": "Trường vku bị ngập lụt",
      "type": "emergency_alert",
      "content": "Thông báo đến các sinh viên trường vku bị ngập lụt, các phương tiện di chuyển có thể bị dán đoạn.",
      "priority": "urgent",
      "notificationChannels": {
        "sms": false,
        "email": true
      },
      "location": {
        "lat": 16.059835720164806,
        "long": 108.2189091559153,
        "address": "Phường Phước Ninh, Hải Châu District, Đà Nẵng, Vietnam"
      }
    }
  ]
}
```

| Params             | Description                           | Default |
| ------------------ | ------------------------------------- | ------- |
| filters            | Object containing filter conditions   | N/A     |
| filters[type]      | Type of alert (e.g., emergency_alert) | N/A     |
| filters[type][$eq] | Comparison operator (equal)           | N/A     |
| value              | Value to compare (emergency_alert)    | N/A     |

#### 2. Create a New Emergency Alert

- **Endpoint**: `POST /api/communities`
- **Description**: Create a new emergency notification from community.
- **Body**:

```json
{
  "data": {
    "title": "Trường vku bị ngập lụt",
    "type": "emergency_alert",
    "content": "Thông báo đến các sinh viên trường vku bị ngập lụt, các phương tiện di chuyển có thể bị dán đoạn.",
    "priority": "urgent",
    "notificationChannels": {
      "sms": false,
      "email": true
    },
    "location": {
      "lat": 16.059835720164806,
      "long": 108.2189091559153,
      "address": "Phường Phước Ninh, Hải Châu District, Đà Nẵng, Vietnam"
    }
  }
}
```

| Body                 | Description                         | Required |
| -------------------- | ----------------------------------- | -------- |
| title                | Title of the alert                  | true     |
| type                 | Type of alert (emergency_alert)     | true     |
| content              | Content of the alert                | true     |
| priority             | Priority level (urgent, normal)     | true     |
| notificationChannels | Notification channels (sms, email)  | true     |
| location             | Alert location (lat, long, address) | true     |

#### 3. Get All Document Guides

- **Endpoint**: `GET /api/communities`
- **Description**: Retrieve all document guides such as safety guide, evacuation guide, and first aid guide.

| Params                              | Description                       | Default |
| ----------------------------------- | --------------------------------- | ------- |
| filters[type][$eq]=safety_guide     | Get All Safety Guide document     | Null    |
| filters[type][$eq]=evacuation_guide | Get All Evacuation Guide document | Null    |
| filters[type][$eq]=first_aid_guide  | Get All First Aid Guide document  | Null    |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make changes and commit (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the terms of the [Apache V2.0](LICENSE)
