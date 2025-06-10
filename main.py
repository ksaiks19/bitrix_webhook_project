from fastapi import FastAPI, Request
import logging

app = FastAPI()

@app.post("/bitrix-webhook")
async def handle_bitrix_webhook(request: Request):
    data = await request.json()
    logging.warning(f"Received Bitrix data: {data}")
    return {"status": "received"}
