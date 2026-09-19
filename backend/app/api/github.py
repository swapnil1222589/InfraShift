import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.core.config import settings
from app.services.github_service import process_webhook

router = APIRouter()

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    
    if not settings.MOCK_GITHUB and settings.GITHUB_WEBHOOK_SECRET:
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        mac = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + mac.hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()
    await process_webhook(data, background_tasks)
    return {"status": "received"}
