# Quotex Historical Data API
This is a complete API for Quotex OHLCV historical and live data, created by Haider!

## Features
- Unlimited historical candle data (bypasses Quotex limits)
- Simple endpoint like: `/quotex_candles?asset=USDBDT_otc&timeframe=M1&count=500`
- 24/7 hosting ready

## Endpoint
`GET /quotex_candles?asset=ASSET&timeframe=TIMEFRAME&count=COUNT`

Parameters:
- `asset`: Asset pair (e.g., USDBDT_otc, EURUSD_otc)
- `timeframe`: M1, M5, M15, M30, H1, H4, D1
- `count`: Number of candles (100, 500, 1000+)

## Hosting on Render
1. Upload the entire folder to GitHub
2. Connect your GitHub repo to Render
3. Use the `render.yaml` file for auto-configuration
4. Your API will be at: `https://quotex-api-haider.onrender.com`
