"""
Create a Vapi voice assistant that uses AssemblyAI for speech-to-text.

Two transcriber options:
  builtin  Vapi's AssemblyAI provider ("assembly-ai"). As of Nov 16, 2026 it lists
           universal-3-6-pro (Universal-3.6 Pro Realtime, the previous flagship,
           still fully supported) and universal-3-5-pro.
  custom   Vapi's custom transcriber, pointed at custom_transcriber.py, which
           streams the caller's audio to AssemblyAI STT 3.7 Realtime Agent
           (assemblyai-stt-3-7-realtime-agent).

Usage:
  python create_assistant.py create --transcriber custom
  python create_assistant.py call --assistant-id <id> --phone +1XXXXXXXXXX
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.environ["VAPI_API_KEY"]
HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json",
}
BASE_URL = "https://api.vapi.ai"

FIRST_MESSAGE = "Hi, thanks for calling Acme Insurance. Can I get your policy number?"
KEYTERMS = ["Acme Insurance", "Gold plan", "deductible", "prior authorization"]


def builtin_transcriber() -> dict:
    """Vapi's built-in AssemblyAI provider (fields from Vapi's AssemblyAI docs)."""
    return {
        "provider": "assembly-ai",
        "speechModel": "universal-3-6-pro",
        "mode": "balanced",
        "keytermsPrompt": KEYTERMS,
        # Seed the first turn with the greeting, then let Vapi send each
        # assistant reply to AssemblyAI as agent context automatically.
        "agentContext": FIRST_MESSAGE,
        "agentContextAutoUpdateEnabled": True,
    }


def custom_transcriber() -> dict:
    """Vapi custom transcriber -> custom_transcriber.py -> AssemblyAI STT 3.7 Realtime Agent."""
    server = {"url": os.environ["CUSTOM_TRANSCRIBER_URL"]}  # wss://<host>/api/custom-transcriber
    if os.getenv("TRANSCRIBER_SECRET"):
        server["headers"] = {"x-transcriber-secret": os.environ["TRANSCRIBER_SECRET"]}
    return {"provider": "custom-transcriber", "server": server}


def create_assistant(transcriber: str = "custom", name: str = "AssemblyAI Demo Assistant") -> dict:
    """Create a Vapi assistant with AssemblyAI as the transcriber."""

    payload = {
        "name": name,

        # ── STT: AssemblyAI ───────────────────────────────────────────────
        "transcriber": custom_transcriber() if transcriber == "custom" else builtin_transcriber(),

        # ── LLM ───────────────────────────────────────────────────────────
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, helpful phone assistant for Acme Insurance. "
                        "Keep every response under 2–3 sentences. "
                        "Speak naturally, with no markdown or lists."
                    ),
                }
            ],
            "temperature": 0.7,
            "maxTokens": 200,
        },

        # ── Call behaviour ────────────────────────────────────────────────
        "firstMessage": FIRST_MESSAGE,
        "endCallMessage": "Thanks for calling. Have a great day!",
        "endCallPhrases": ["goodbye", "bye", "hang up", "end call"],
        "maxDurationSeconds": 600,
    }

    resp = requests.post(f"{BASE_URL}/assistant", headers=HEADERS, json=payload)
    resp.raise_for_status()
    assistant = resp.json()
    print(f"✅ Created assistant: {assistant['id']}")
    print(json.dumps(assistant, indent=2))
    return assistant


def make_outbound_call(phone_number: str, assistant_id: str) -> dict:
    """Make an outbound call using the assistant."""

    payload = {
        "assistantId": assistant_id,
        "phoneNumber": {
            "twilioPhoneNumber": os.environ["TWILIO_PHONE_NUMBER"],
            "twilioAccountSid": os.environ["TWILIO_ACCOUNT_SID"],
            "twilioAuthToken": os.environ["TWILIO_AUTH_TOKEN"],
        },
        "customer": {
            "number": phone_number,
        },
    }

    resp = requests.post(f"{BASE_URL}/call", headers=HEADERS, json=payload)
    resp.raise_for_status()
    call = resp.json()
    print(f"📞 Call initiated: {call['id']}")
    return call


def list_calls(assistant_id: str, limit: int = 10) -> list:
    """Retrieve recent calls for an assistant."""

    resp = requests.get(
        f"{BASE_URL}/call",
        headers=HEADERS,
        params={"assistantId": assistant_id, "limit": limit},
    )
    resp.raise_for_status()
    calls = resp.json()
    for call in calls:
        print(f"  {call['id']} | {call.get('status')} | {call.get('endedReason', '')}")
    return calls


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new assistant")
    create_parser.add_argument("--transcriber", choices=["custom", "builtin"], default="custom")

    call_parser = subparsers.add_parser("call", help="Make an outbound call")
    call_parser.add_argument("--assistant-id", required=True)
    call_parser.add_argument("--phone", required=True, help="+1XXXXXXXXXX format")

    list_parser = subparsers.add_parser("list-calls", help="List recent calls")
    list_parser.add_argument("--assistant-id", required=True)

    args = parser.parse_args()

    if args.command == "create":
        create_assistant(args.transcriber)
    elif args.command == "call":
        make_outbound_call(args.phone, args.assistant_id)
    elif args.command == "list-calls":
        list_calls(args.assistant_id)
    else:
        parser.print_help()
