"""
Vapi custom transcriber backed by AssemblyAI STT 3.7 Realtime Agent.

Vapi's built-in AssemblyAI transcriber doesn't list the 3.7 models yet, so this
server sits between Vapi and AssemblyAI:

  Vapi call ──(stereo 16-bit PCM over WebSocket)──► this server
                                                        │ customer channel only
                                                        ▼
                               AssemblyAI STT 3.7 Realtime Agent
                                                        │ Turn messages
  Vapi ◄──(transcriber-response: partial / final)───────┘

Run:   uvicorn custom_transcriber:app --host 0.0.0.0 --port 8001
Point: transcriber.server.url = wss://<your-host>/api/custom-transcriber
"""

import asyncio
import json
import os
from urllib.parse import urlencode

import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

load_dotenv()

app = FastAPI(title="Vapi custom transcriber: AssemblyAI STT 3.7 Realtime Agent")

ASSEMBLYAI_API_KEY = os.environ["ASSEMBLYAI_API_KEY"]
AAI_WS_BASE = "wss://streaming.assemblyai.com/v3/ws"

# Optional: domain vocabulary, comma-separated (up to 100 terms)
KEYTERMS = [t.strip() for t in os.getenv("KEYTERMS", "").split(",") if t.strip()]

# Optional shared secret: set the same value in the assistant's
# transcriber.server.headers["x-transcriber-secret"] (see create_assistant.py)
TRANSCRIBER_SECRET = os.getenv("TRANSCRIBER_SECRET")


def assemblyai_url(sample_rate: int) -> str:
    params = [
        ("speech_model", "assemblyai-stt-3-7-realtime-agent"),
        ("encoding", "pcm_s16le"),
        ("sample_rate", sample_rate),
    ]
    if KEYTERMS:
        params.append(("keyterms_prompt", json.dumps(KEYTERMS)))
    return f"{AAI_WS_BASE}?{urlencode(params)}"


def customer_channel(buf: bytes, channels: int) -> tuple[bytes, bytes]:
    """Return (customer audio, leftover bytes) from interleaved 16-bit PCM.

    Vapi sends the customer on channel 0 and the assistant on channel 1.
    Only the customer is sent to AssemblyAI.
    """
    frame = 2 * channels
    usable = len(buf) - len(buf) % frame
    if channels == 1:
        return buf[:usable], buf[usable:]
    samples = memoryview(buf[:usable]).cast("h")
    return samples[0::channels].tobytes(), buf[usable:]


@app.websocket("/api/custom-transcriber")
async def custom_transcriber(vapi_ws: WebSocket):
    if TRANSCRIBER_SECRET and vapi_ws.headers.get("x-transcriber-secret") != TRANSCRIBER_SECRET:
        await vapi_ws.close(code=1008)
        return
    await vapi_ws.accept()

    # Vapi's first text frame describes the audio:
    # {"type": "start", "encoding": "linear16", "container": "raw",
    #  "sampleRate": 16000, "channels": 2}
    start = json.loads(await vapi_ws.receive_text())
    sample_rate = int(start.get("sampleRate", 16000))
    channels = int(start.get("channels", 2))

    async with websockets.connect(
        assemblyai_url(sample_rate),
        additional_headers={"Authorization": ASSEMBLYAI_API_KEY},
    ) as aai_ws:

        async def vapi_to_assemblyai():
            leftover = b""
            try:
                while True:
                    message = await vapi_ws.receive()
                    if message["type"] == "websocket.disconnect":
                        break
                    data = message.get("bytes")
                    if not data:
                        continue  # ignore any further text frames
                    audio, leftover = customer_channel(leftover + data, channels)
                    if audio:
                        await aai_ws.send(audio)
            except WebSocketDisconnect:
                pass
            finally:
                await aai_ws.send(json.dumps({"type": "Terminate"}))

        async def assemblyai_to_vapi():
            async for raw in aai_ws:
                msg = json.loads(raw)
                if msg.get("type") != "Turn":
                    continue
                text = msg.get("transcript", "").strip()
                if not text:
                    continue  # e.g. an empty final
                # Each Turn re-transcribes the whole turn, which matches Vapi's
                # partial semantics: every partial replaces the previous one.
                await vapi_ws.send_text(json.dumps({
                    "type": "transcriber-response",
                    "transcription": text,
                    "channel": "customer",
                    "transcriptType": "final" if msg.get("end_of_turn") else "partial",
                }))

        await asyncio.gather(vapi_to_assemblyai(), assemblyai_to_vapi())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
