# Quotex Live OHLCV API - Complete Guide

## What You Need

1. **Quotex Account Credentials** (email & password)
2. **Python 3.9+** installed
3. **Windows 10/11** (Quotex works best on Windows)

---

## Step 1: Setup

### 1.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.2 Configure Your Credentials
Copy `.env.example` to `.env` and add your Quotex login:
```bash
# Copy the example file
copy .env.example .env

# Now edit .env with your actual email and password
```

Your `.env` file should look like:
```env
QUOTEX_EMAIL=your_actual_email@example.com
QUOTEX_PASSWORD=your_actual_password
```

---

## Step 2: Start the API Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

---

## Step 3: Use the API

### API Documentation (Auto-Generated!)
Visit these URLs in your browser:
- **Swagger UI**: `http://localhost:8000/docs` (interactive testing!)
- **ReDoc**: `http://localhost:8000/redoc`

---

## Available Endpoints

### 1. Check Status
```http
GET /
```
Returns if the API is connected to Quotex.

### 2. Get All Assets
```http
GET /assets
```
Lists all available trading assets with their codes and payouts.

### 3. Get Historical OHLCV Data
```http
POST /historical
Content-Type: application/json

{
  "asset": "USDPKR_otc",
  "period": 60,
  "days": 1.0
}
```
- `asset`: Asset code (e.g., "USDPKR_otc", "EURUSD_otc")
- `period`: Timeframe in seconds (60=1m, 300=5m, 900=15m, 3600=1h, etc.)
- `days`: Number of days of history to fetch

**Response Example**:
```json
[
  {
    "time": 1234567890,
    "open": 280.50,
    "high": 281.20,
    "low": 279.80,
    "close": 280.90,
    "ticks": 45
  }
]
```

### 4. Get Realtime Data
```http
GET /realtime/{asset}?period=60
```
Example: `http://localhost:8000/realtime/USDPKR_otc?period=60`

### 5. Force Reconnect
```http
POST /connect
```
Use this if connection drops.

### 6. Health Check
```http
GET /health
```

---

## Common Asset Codes

Here are some popular assets:
- `USDPKR_otc` - USD/PKR OTC
- `EURUSD_otc` - EUR/USD OTC
- `GBPUSD_otc` - GBP/USD OTC
- `USDJPY_otc` - USD/JPY OTC
- `XAUUSD_otc` - Gold OTC
- `BTCUSD_otc` - Bitcoin OTC

Use `GET /assets` to see all available assets.

---

## Using with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Get historical data
response = requests.post(f"{BASE_URL}/historical", json={
    "asset": "USDPKR_otc",
    "period": 60,
    "days": 1
})
data = response.json()
print(data)

# Get realtime data
response = requests.get(f"{BASE_URL}/realtime/USDPKR_otc?period=60")
print(response.json())
```

---

## Using with JavaScript (Fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// Get historical data
fetch(`${BASE_URL}/historical`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        asset: "USDPKR_otc",
        period: 60,
        days: 1
    })
})
.then(r => r.json())
.then(data => console.log(data));

// Get realtime data
fetch(`${BASE_URL}/realtime/USDPKR_otc?period=60`)
.then(r => r.json())
.then(data => console.log(data));
```

---

## Troubleshooting

1. **Connection Failed?**
   - Double-check your email/password in `.env`
   - Try `POST /connect` to reconnect
   - Check your internet connection

2. **No Data for Asset?**
   - Use `GET /assets` to find the correct asset code
   - Try adding `_otc` suffix (or removing it)

3. **Port Already in Use?**
   - Change the port: `uvicorn main:app --port 8001`

---

## Features Included

✅ Complete FastAPI server with automatic docs  
✅ Historical data fetching (bypasses 199-candle limit)  
✅ Realtime OHLCV data  
✅ CORS enabled for frontend integration  
✅ Health check endpoints  
✅ Asset listing with payout information  
✅ Auto-connection management  
✅ Proper error handling  

The API is **fully completed** and ready to use!
