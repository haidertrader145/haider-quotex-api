"""
Quotex Live OHLCV API
A complete FastAPI server for live and historical OHLCV data from Quotex
"""
import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the current directory to path
import sys
sys.path.insert(0, ".")

from pyquotex.stable_api import Quotex

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Quotex Live OHLCV API",
    description="API for live and historical OHLCV data from Quotex",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
quotex_client: Optional[Quotex] = None
is_connected = False

# Pydantic models
class OHLCVCandle(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    ticks: Optional[int] = 0

class HistoricalDataRequest(BaseModel):
    asset: str
    period: int = 60
    days: float = 1.0

class APIStatus(BaseModel):
    connected: bool
    email: Optional[str] = None
    timestamp: float

class AssetInfo(BaseModel):
    name: str
    code: str
    open: bool

# Helper functions
def get_client() -> Quotex:
    """Get the Quotex client instance"""
    global quotex_client
    if quotex_client is None:
        email = os.getenv("QUOTEX_EMAIL")
        password = os.getenv("QUOTEX_PASSWORD")
        host = os.getenv("QUOTEX_HOST", "qxbroker.com")
        if not email or not password:
            raise HTTPException(status_code=500, detail="QUOTEX_EMAIL and QUOTEX_PASSWORD must be set in .env")
        quotex_client = Quotex(email=email, password=password, host=host, lang="en")
        quotex_client.debug_ws_enable = False
    return quotex_client

async def ensure_connected():
    """Ensure we're connected to Quotex"""
    global is_connected, quotex_client
    client = get_client()
    if not is_connected:
        print("Connecting to Quotex...")
        check, msg = await client.connect()
        if not check:
            raise HTTPException(status_code=500, detail=f"Failed to connect: {msg}")
        is_connected = True
        print("Connected successfully!")
    return client

# API Routes
@app.on_event("startup")
async def startup_event():
    """Connect to Quotex on API startup"""
    try:
        await ensure_connected()
    except Exception as e:
        print(f"Startup connection failed: {e}")
        print("Will try to connect on first request...")

@app.get("/", response_model=APIStatus)
async def root():
    """Get API status"""
    return APIStatus(
        connected=is_connected,
        email=os.getenv("QUOTEX_EMAIL"),
        timestamp=time.time()
    )

@app.post("/connect")
async def connect():
    """Force (re-)connect to Quotex"""
    global is_connected, quotex_client
    is_connected = False
    quotex_client = None
    try:
        await ensure_connected()
        return {"status": "connected", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assets", response_model=List[Dict])
async def get_assets():
    """Get list of available assets"""
    client = await ensure_connected()
    instruments = await client.get_instruments()
    assets = []
    for inst in instruments:
        if inst[0]:
            assets.append({
                "code": inst[1],
                "name": inst[2].replace("\n", ""),
                "open": inst[14],
                "payout_1m": inst[-9],
                "payout_5m": inst[-8]
            })
    return assets

@app.post("/historical", response_model=List[OHLCVCandle])
async def get_historical_data(request: HistoricalDataRequest):
    """
    Get historical OHLCV data
    - asset: Asset code (e.g., "USDPKR_otc", "EURUSD_otc")
    - period: Timeframe in seconds (60=1m, 300=5m, etc.)
    - days: Number of days of history to fetch
    """
    client = await ensure_connected()
    
    # Get asset (handle OTC automatically)
    asset_name, asset_data = await client.get_available_asset(request.asset, force_open=True)
    
    amount_of_seconds = int(request.days * 86400)
    candles = await client.get_candles_deep(
        asset_name, 
        amount_of_seconds, 
        request.period
    )
    
    # Clean and validate candles
    cleaned_candles = []
    for c in candles:
        if c.get("open") is not None and c.get("close") is not None:
            cleaned_candles.append({
                "time": c["time"],
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),
                "ticks": c.get("ticks", 0)
            })
    
    return cleaned_candles

@app.get("/realtime/{asset}")
async def get_realtime_data(asset: str, period: int = 60):
    """
    Get realtime OHLCV data (last candle)
    - asset: Asset code
    - period: Timeframe in seconds
    """
    client = await ensure_connected()
    
    asset_name, _ = await client.get_available_asset(asset, force_open=True)
    
    # Start streaming
    client.start_candles_stream(asset_name, period)
    
    # Get recent candles
    candles = await client.get_candles(asset_name, time.time(), 3600, period)
    
    if candles:
        last_candle = candles[-1]
        return {
            "asset": asset_name,
            "period": period,
            "candle": {
                "time": last_candle["time"],
                "open": float(last_candle["open"]),
                "high": float(last_candle["high"]),
                "low": float(last_candle["low"]),
                "close": float(last_candle["close"]),
                "ticks": last_candle.get("ticks", 0)
            },
            "datetime": datetime.fromtimestamp(last_candle["time"]).isoformat()
        }
    else:
        raise HTTPException(status_code=404, detail="No data available")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "connected": is_connected,
        "timestamp": time.time()
    }

@app.get("/quotex_candles")
async def get_quotex_candles(
    asset: str = "USDBDT_otc",
    timeframe: str = "M1",
    count: int = 100
):
    """
    Simple endpoint like your example!
    Example: /quotex_candles?asset=USDBDT_otc&timeframe=M1&count=500
    """
    client = await ensure_connected()
    
    # Map timeframe to seconds
    timeframe_map = {
        "M1": 60,
        "M5": 300,
        "M15": 900,
        "M30": 1800,
        "H1": 3600,
        "H4": 14400,
        "D1": 86400
    }
    period = timeframe_map.get(timeframe, 60)
    
    # Calculate days needed
    candles_needed = max(count, 100)
    days_needed = (candles_needed * period) / 86400 + 0.1  # Add a little extra
    
    # Get asset
    asset_name, _ = await client.get_available_asset(asset, force_open=True)
    
    # Get candles
    all_candles = await client.get_candles_deep(
        asset_name,
        int(days_needed * 86400),
        period
    )
    
    # Take last N candles and format like your example
    formatted = []
    candles = all_candles[-count:] if len(all_candles) >= count else all_candles
    
    for i, candle in enumerate(reversed(candles)):
        open_price = candle.get("open")
        close_price = candle.get("close")
        
        if open_price is None or close_price is None:
            continue
            
        color = "green" if close_price > open_price else "red" if close_price < open_price else "gray"
        dt = datetime.fromtimestamp(candle["time"])
        
        formatted.append({
            "id": str(i + 1),
            "pair": asset_name,
            "timeframe": timeframe,
            "candle_time": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": candle["time"],
            "open": str(open_price),
            "high": str(candle.get("high", open_price)),
            "low": str(candle.get("low", open_price)),
            "close": str(close_price),
            "volume": str(candle.get("ticks", 0)),
            "color": color,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return formatted

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
