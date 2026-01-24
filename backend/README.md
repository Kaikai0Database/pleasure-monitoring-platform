# Flask 後端 API

失樂感監測平台的 Python Flask 後端服務。

## 功能

- 用戶註冊與登入（JWT 認證）
- 評估歷史記錄管理
- 數據按用戶隔離
- CORS 支援前端請求

## 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

## 啟動伺服器

```bash
python run.py
```

伺服器將在 `http://localhost:5000` 啟動

## API 端點

### 健康檢查

**GET** `/api/health`
```json
Response: {"status": "ok", "message": "Flask backend is running"}
```

### 認證

**POST** `/api/auth/register`
```json
Request: {
  "email": "user@example.com",
  "name": "User Name",
  "password": "password123"
}
Response: {
  "success": true,
  "message": "註冊成功",
  "user": {"id": 1, "email": "...", "name": "..."}
}
```

**POST** `/api/auth/login`
```json
Request: {
  "email": "user@example.com",
  "password": "password123"
}
Response: {
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {"id": 1, "email": "...", "name": "..."}
}
```

**GET** `/api/auth/me`
```json
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "success": true,
  "user": {"id": 1, "email": "...", "name": "..."}
}
```

### 歷史記錄

**GET** `/api/history`
```json
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "success": true,
  "history": [...]
}
```

**POST** `/api/history`
```json
Headers: {"Authorization": "Bearer <token>"}
Request: {
  "total_score": 25,
  "max_score": 56,
  "level": "良好",
  "answers": [{"questionId": 1, "emoji": "😄", "score": 1}, ...]
}
Response: {
  "success": true,
  "history_id": 1,
  "message": "評估結果已保存"
}
```

**DELETE** `/api/history/<id>`
```json
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "success": true,
  "message": "記錄已刪除"
}
```

## 測試

使用 Thunder Client、Postman 或 curl 測試 API：

```bash
# 健康檢查
curl http://localhost:5000/api/health

# 註冊用戶
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test123"}'

# 登入
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 數據庫

使用 SQLite（開發環境）
- 位置: `instance/database.db`
- 自動創建表結構

## 環境變數

編輯 `.env` 文件配置：
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT token 加密密鑰
- `SQLALCHEMY_DATABASE_URI`: 數據庫連接字符串
