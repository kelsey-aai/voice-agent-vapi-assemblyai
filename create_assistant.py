"""
Create a Vapi voice assistant using AssemblyAI as the transcriber.

Demonstrates:
  - Creating an assistant via the Vapi REST API
  - Configuring AssemblyAI Universal-3.5 Pro Realtime as the transcriber
  - Keyterm prompting for domain-specific vocabulary
  - Making an outbound test call
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


def create_assistant(name: str = "AssemblyAI Demo Assistant") -> dict:
    """Create a Vapi assistant with AssemblyAI Universal-3.5 Pro Realtime as STT."""

    payload = {
        "name": name,

        # ── STT: AssemblyAI Universal-3.5 Pro Realtime ────────────────────
        # Use "assembly-ai" provider + "universal-3-5-pro" model to enable
        # Universal-3.5 Pro Realtime (select in dashboard, or set via API).
        "transcriber": {
            "provider": "assembly-ai",
            "model": "universal-3-5-pro",
            "language": "en",
            # Boost recognition for domain-specific terms (up to 100 keyterms).
            # Each term: up to 50 characters. Optional soundsLike for phonetics.
            "keytermsPrompt": [
                "AssemblyAI",
                "Universal-3",
                "voice agent",
            ],
            # Emit turn when end-of-turn confidence passes this threshold.
            "confidenceThreshold": 0.4,
        },

        # ── LLM ───────────────────────────────────────────────────────────
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, helpful voice assistant. "
                        "Keep every response under 2–3 sentences. "
                        "Speak naturally — no markdown or lists."
                    ),
                }
            ],
            "temperature": 0.7,
            "maxTokens": 200,
        },

        # ── TTS ───────────────────────────────────────────────────────────
        "voice": {
            "provider": "playht",
            "voiceId": "jennifer",
        },

        # ── Call behaviour ────────────────────────────────────────────────
        "firstMessage": "Hi! I'm your AI assistant powered by AssemblyAI. How can I help you today?",
        "endCallMessage": "Thanks for calling. Have a great day!",
        "endCallPhrases": ["goodbye", "bye", "hang up", "end call"],

        # ── Silence / interruption ────────────────────────────────────────
        "silenceTimeoutSeconds": 30,
        "maxDurationSeconds": 600,
        "backgroundDenoisingEnabled": True,
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

    resp = requests.post(f"{BASE_URL}/call/phone", headers=HEADERS, json=payload)
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

    subparsers.add_parser("create", help="Create a new assistant")

    call_parser = subparsers.add_parser("call", help="Make an outbound call")
    call_parser.add_argument("--assistant-id", required=True)
    call_parser.add_argument("--phone", required=True, help="+1XXXXXXXXXX format")

    list_parser = subparsers.add_parser("list-calls", help="List recent calls")
    list_parser.add_argument("--assistant-id", required=True)

    args = parser.parse_args()

    if args.command == "create":
        create_assistant()
    elif args.command == "call":
        make_outbound_call(args.phone, args.assistant_id)
    elif args.command == "list-calls":
        list_calls(args.assistant_id)
    else:
        parser.print_help()
