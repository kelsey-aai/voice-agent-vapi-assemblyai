"""
Vapi webhook server — receive call events and transcripts.

Run with: uvicorn webhook_server:app --port 8000
Configure in Vapi dashboard: Settings > Webhooks > Server URL = https://your-url/webhook
"""

import hashlib
import hmac
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

app = FastAPI(title="Vapi Webhook Handler")

VAPI_WEBHOOK_SECRET = os.getenv("VAPI_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify Vapi webhook HMAC-SHA256 signature."""
    if not VAPI_WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    expected = hmac.new(
        VAPI_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-vapi-signature", "")

    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = json.loads(body)
    event_type = event.get("message", {}).get("type")

    handlers = {
        "call-start": handle_call_start,
        "call-end": handle_call_end,
        "transcript": handle_transcript,
        "end-of-call-report": handle_end_of_call_report,
        "status-update": handle_status_update,
    }

    handler = handlers.get(event_type)
    if handler:
        await handler(event["message"])

    return {"status": "ok"}


async def handle_call_start(msg: dict):
    call_id = msg.get("call", {}).get("id")
    print(f"📞 Call started: {call_id}")


async def handle_call_end(msg: dict):
    call = msg.get("call", {})
    print(f"📵 Call ended: {call.get('id')} | reason: {call.get('endedReason')}")


async def handle_transcript(msg: dict):
    """Real-time transcript from AssemblyAI Universal Streaming."""
    role = msg.get("role")          # "user" or "assistant"
    transcript = msg.get("transcript")
    transcript_type = msg.get("transcriptType")  # "partial" or "final"

    if transcript_type == "final":
        icon = "👤" if role == "user" else "🤖"
        print(f"{icon} [{role}]: {transcript}")


async def handle_end_of_call_report(msg: dict):
    """Full call report with complete transcript and summary."""
    call = msg.get("call", {})
    summary = msg.get("summary", "No summary available")
    transcript = msg.get("transcript", "")

    print(f"\n{'='*60}")
    print(f"📋 Call Report: {call.get('id')}")
    print(f"Duration: {call.get('duration', 0):.0f}s")
    print(f"Ended reason: {call.get('endedReason')}")
    print(f"\nSummary:\n{summary}")
    print(f"\nFull transcript:\n{transcript}")
    print("="*60)


async def handle_status_update(msg: dict):
    status = msg.get("status")
    call_id = msg.get("call", {}).get("id")
    print(f"⚡ Status update — call {call_id}: {status}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
