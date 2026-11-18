# Vapi voice agent with AssemblyAI STT 3.7 Realtime Agent

Companion code for the blog post **[Vapi voice agent with AssemblyAI STT 3.7 Realtime Agent](https://www.assemblyai.com/blog/vapi-voice-agent-with-assemblyai)**.

Vapi is one of the fastest ways to get a voice agent onto a real phone number. It handles telephony, turn-taking and orchestration, and it lets you choose the speech-to-text provider, so the decision that matters is which model does the listening.

That choice matters more than it looks. Your LLM can only reason about the text it receives, and your TTS can only read back what the LLM wrote. Get a policy number wrong at the transcriber and the whole turn is wrong, confidently and fluently.

This guide covers two ways to use [AssemblyAI streaming speech-to-text](https://www.assemblyai.com/products/streaming-speech-to-text) in a Vapi assistant:

1. **Vapi's custom transcriber**, pointed at a small bridge server, which runs AssemblyAI STT 3.7 Realtime Agent (`assemblyai-stt-3-7-realtime-agent`) today.
2. **Vapi's built-in AssemblyAI provider**, which is a dropdown in the dashboard. As of November 16, 2026, it lists Universal-3.6 Pro Realtime (`universal-3-6-pro`), the previous flagship, which is still fully supported, and Universal-3.5 Pro Realtime. It doesn't list the 3.7 models yet.

## Why AssemblyAI STT 3.7 Realtime Agent for a Vapi agent?

STT 3.7 Realtime Agent is the model the AssemblyAI docs recommend for [voice agents](https://www.assemblyai.com/solutions/voice-agents). It's trained on real voice-agent and telephony conversations in which every speaker's role is labeled. For each turn, it uses what the agent and the caller said earlier, plus the most relevant audio from earlier in the call, to tell the caller apart from background speech.

Here's how it compares with other streaming systems on AssemblyAI's English voice-agent benchmark (12,460 scenarios, 522 speakers, telephony audio with no, low or heavy noise). Lower is better in every row:

<table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:15px;">
  <thead>
    <tr style="background-color:#1E56A0; color:#fff;">
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">Metric</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">AssemblyAI STT 3.7 Realtime Agent</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">Soniox Realtime v6</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">ElevenLabs Scribe v3</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">Deepgram Nova-3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Normalized word error rate</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">4.42%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">5.95%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">7.32%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">8.61%</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Word error rate, heavy background noise</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">5.07%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">6.58%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">8.75%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">9.85%</td>
    </tr>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Entity error rate, all entities</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">13.25%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">16.54%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">18.47%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">28.71%</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Names</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">10.11%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">12.47%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">14.01%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">23.73%</td>
    </tr>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Email addresses</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">15.26%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">17.98%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">17.54%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">34.08%</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Dates and times</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">17.67%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">26.14%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">30.09%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">43.88%</td>
    </tr>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Phone numbers</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">6.75%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">6.22%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">7.10%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">10.21%</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Codes and identifiers</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">12.24%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">12.03%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">14.35%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">32.80%</td>
    </tr>
  </tbody>
</table>


*Source: AssemblyAI's voice-agent benchmark, Table 6 of the [AssemblyAI STT 3.7 Realtime Agent research post](https://www.assemblyai.com/blog/assemblyai-stt-3-7-realtime-agent-research), Nov 2026. All systems were scored on the recordings every system completed, with the same normalizer.*

Among the streaming systems measured, STT 3.7 Realtime Agent has the lowest normalized word error rate, 26% below the next provider, and it's the lowest at every noise level. Its entity error rate is also the lowest, 20% below the next provider. It isn't first everywhere: Soniox Realtime v6 is slightly ahead on phone numbers and on codes and identifiers. It also drops the fewest one- and two-word replies of any system measured, and no measured system has both less background-speech leakage and fewer dropped short replies.

Compared with Universal-3.6 Pro Realtime, the model in Vapi's dropdown today, STT 3.7 Realtime Agent makes 80% fewer number errors on Voice Code Bench (11.28% → 2.27%). It adds 47% fewer words while the caller is silent (2.53 → 1.34 per 1,000 words), drops 38% fewer short replies (0.29% → 0.18%), and has 12% fewer false end-of-turn events. A single WER figure hides most of this, which is why we've argued that [word error rate alone is broken](https://www.assemblyai.com/blog/word-error-rate-is-broken) as a buying metric for agents.

## Two ways to plug AssemblyAI into Vapi

<table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:15px;">
  <thead>
    <tr style="background-color:#1E56A0; color:#fff;">
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;"></th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">Custom transcriber (this guide's bridge)</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">Vapi's built-in AssemblyAI provider</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Speech model</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">assemblyai-stt-3-7-realtime-agent</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">universal-3-6-pro or universal-3-5-pro (as of Nov 16, 2026)</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Setup</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">Run a small WebSocket server; set transcriber.provider to custom-transcriber</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">Pick AssemblyAI in the dashboard, or set provider assembly-ai</td>
    </tr>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Agent context</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">Earlier caller turns carried forward by the model</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">agentContext plus automatic updates after each assistant turn</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Billing for speech-to-text</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">Your AssemblyAI account, $0.45/hr</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">Your AssemblyAI key, added in Vapi</td>
    </tr>
  </tbody>
</table>


If you want the newest model in production this week, use the custom transcriber. If you want zero extra infrastructure, use the built-in provider and switch models when Vapi adds 3.7.


## Quick start

Clone the reference repo:

```bash
git clone https://github.com/kelsey-aai/voice-agent-vapi-assemblyai
cd voice-agent-vapi-assemblyai
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and add your Vapi and AssemblyAI keys. If you don't have an AssemblyAI key yet, [grab a free one](https://www.assemblyai.com/dashboard/signup).

## Option 1: run AssemblyAI STT 3.7 Realtime Agent through a custom transcriber

Vapi's [custom transcriber](https://docs.vapi.ai/customization/custom-transcriber) lets you plug any streaming speech-to-text service into an assistant. Vapi opens a WebSocket to your server and sends a `start` message, then streams the call as raw 16-bit PCM in two channels: the caller on channel 0 and the assistant on channel 1. Your server sends back `transcriber-response` messages, either `partial` or `final`.

That maps cleanly onto the AssemblyAI streaming API. The bridge takes channel 0, streams it to STT 3.7 Realtime Agent, and turns each `Turn` message into a Vapi response. Every AssemblyAI `Turn` re-transcribes the whole turn, which is exactly how Vapi treats partials: each one replaces the last until the final arrives.

### The bridge

```python
"""Vapi custom transcriber backed by AssemblyAI STT 3.7 Realtime Agent."""

import asyncio
import json
import os
from urllib.parse import urlencode

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

ASSEMBLYAI_API_KEY = os.environ["ASSEMBLYAI_API_KEY"]
KEYTERMS = [t.strip() for t in os.getenv("KEYTERMS", "").split(",") if t.strip()]


def assemblyai_url(sample_rate: int) -> str:
    params = [
        ("speech_model", "assemblyai-stt-3-7-realtime-agent"),
        ("encoding", "pcm_s16le"),
        ("sample_rate", sample_rate),
    ]
    if KEYTERMS:
        params.append(("keyterms_prompt", json.dumps(KEYTERMS)))
    return f"wss://streaming.assemblyai.com/v3/ws?{urlencode(params)}"


def customer_channel(buf: bytes, channels: int) -> tuple[bytes, bytes]:
    """Return (caller audio, leftover bytes) from interleaved 16-bit PCM."""
    frame = 2 * channels
    usable = len(buf) - len(buf) % frame
    if channels == 1:
        return buf[:usable], buf[usable:]
    samples = memoryview(buf[:usable]).cast("h")
    return samples[0::channels].tobytes(), buf[usable:]


@app.websocket("/api/custom-transcriber")
async def custom_transcriber(vapi_ws: WebSocket):
    await vapi_ws.accept()

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
                        continue
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
                text = msg.get("transcript", "").strip()
                if msg.get("type") != "Turn" or not text:
                    continue
                await vapi_ws.send_text(json.dumps({
                    "type": "transcriber-response",
                    "transcription": text,
                    "channel": "customer",
                    "transcriptType": "final" if msg.get("end_of_turn") else "partial",
                }))

        await asyncio.gather(vapi_to_assemblyai(), assemblyai_to_vapi())
```

Run it and expose it with a tunnel during development:

```bash
uvicorn custom_transcriber:app --host 0.0.0.0 --port 8001
ngrok http 8001
```

The repo version also checks an optional shared-secret header. For production, Vapi recommends authenticating custom transcriber endpoints with Custom Credentials (`credentialId`).

### Point the assistant at it

Set the assistant's transcriber to `custom-transcriber` with your bridge's URL:

```json
{
  "transcriber": {
    "provider": "custom-transcriber",
    "server": {
      "url": "wss://your-ngrok-url.ngrok.io/api/custom-transcriber"
    }
  }
}
```

The repo does this for you:

```bash
python create_assistant.py create --transcriber custom
python create_assistant.py call --assistant-id <id> --phone +1XXXXXXXXXX
```

Because the bridge owns the AssemblyAI connection, every streaming parameter is yours to set: keyterms, `mode`, Voice Focus, and on this model `mode=manual`. Keep turn-taking in Vapi's hands unless you have a reason not to; Vapi acts on the finals you send.

## Option 2: use Vapi's built-in AssemblyAI provider

To start without a bridge, first add your AssemblyAI key to Vapi under **Integrations** in the [Vapi dashboard](https://dashboard.vapi.ai). Then open **Assistants**, select your assistant, open the **Transcriber** card, set the **Model** menu's provider filter to **AssemblyAI**, and pick a model.

In the API, the transcriber block uses the fields from Vapi's [AssemblyAI provider page](https://docs.vapi.ai/providers/transcriber/assembly-ai):

```json
{
  "transcriber": {
    "provider": "assembly-ai",
    "speechModel": "universal-3-6-pro",
    "mode": "balanced",
    "keytermsPrompt": ["Acme Insurance", "Gold plan", "deductible"],
    "agentContext": "Hi, thanks for calling Acme Insurance. Can I get your policy number?",
    "agentContextAutoUpdateEnabled": true
  }
}
```

Only `provider` and `speechModel` are required. `agentContext` seeds the first turn, so set it to your assistant's first message. With `agentContextAutoUpdateEnabled`, Vapi sends each assistant reply to AssemblyAI after every assistant turn, so the caller's answer is transcribed in the context of the question it answers. Leave `languageCodes` off to keep automatic detection and code switching, or pass codes such as `["en", "es"]` to steer it.

When Vapi adds the 3.7 models to this provider, switching should be a change to `speechModel`. Check Vapi's provider page for the exact value before you change it.

```bash
python create_assistant.py create --transcriber builtin
```


## Keyterm prompting

Keyterms prime the model for vocabulary it would otherwise have to guess at: product names, plan tiers, internal system names, the ways your customers say your company name. You get up to 100 per session. In the built-in provider, they go in `keytermsPrompt`. In the bridge, they go in the `KEYTERMS` environment variable, which becomes `keyterms_prompt` on the AssemblyAI connection. Our [keyterm prompting guide](https://www.assemblyai.com/blog/keyterm-prompting-real-time-accuracy) covers how to pick them.

The mistake teams make is loading the list with common English words. Spend the slots on the terms a general model has never seen in your context: SKUs, agent names, the branded plan your support line gets asked about forty times a day.

## When to choose AssemblyAI over Deepgram in Vapi

Vapi lets you swap transcribers per assistant, which makes this an easy experiment. Here's how the numbers above read for the two most common choices:

<table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:15px;">
  <thead>
    <tr style="background-color:#1E56A0; color:#fff;">
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">What you're optimizing for</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">AssemblyAI STT 3.7 Realtime Agent</th>
      <th style="padding:10px 14px; text-align:left; border:1px solid #ccc;">Deepgram Nova-3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Overall accuracy on voice-agent audio (normalized WER)</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">4.42%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">8.61%</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Account numbers, emails and other entities</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">13.25% entity error rate</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">28.71%</td>
    </tr>
    <tr>
      <td style="padding:10px 14px; border:1px solid #ccc;">Codes and identifiers</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">12.24%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">32.80%</td>
    </tr>
    <tr style="background-color:#f5f5f5;">
      <td style="padding:10px 14px; border:1px solid #ccc;">Heavy background noise (WER)</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">5.07%</td>
      <td style="padding:10px 14px; border:1px solid #ccc;">9.85%</td>
    </tr>
  </tbody>
</table>


*All figures from AssemblyAI's voice-agent benchmark, Table 6 of the research post. Lower is better.*

If your callers speak a language outside the 32 that STT 3.7 Realtime Agent covers, run the comparison on your own recordings before you commit.

## What this costs

AssemblyAI STT 3.7 Realtime Agent is $0.45/hr, billed on session duration, with keyterm prompting included. On the custom transcriber path, that's billed to your AssemblyAI account. Vapi's platform fee and your LLM and TTS providers bill separately; that's the trade-off of assembling a stack. Current rates for every add-on are on the [pricing page](https://www.assemblyai.com/pricing).

## When you'd skip the orchestrator

Worth saying plainly, because it's a real fork in the road.

Vapi is the right call when you want telephony, a visual builder, a workflow layer and a large integration catalog handed to you, and when the ability to swap any component later is worth managing several vendors now. That's a lot of teams; if you're still choosing a platform, see our comparison of [Vapi vs Pipecat vs LiveKit](https://www.assemblyai.com/blog/vapi-vs-pipecat-vs-livekit).

The other shape is a loop you own: STT 3.7 Realtime Agent for speech-to-text and the [AssemblyAI Text-to-Speech API](https://www.assemblyai.com/products/text-to-speech) for the voice, with your LLM in between, on one bill and one set of logs. The [Node.js voice agent tutorial](https://www.assemblyai.com/blog/node-js-voice-agent-with-assemblyai) builds that loop in a few hundred lines, and the [Twilio phone agent tutorial](https://www.assemblyai.com/blog/twilio-phone-agent-with-assemblyai) puts it on a phone number. If you've hit the point where [your stack's seams are what's slowing you down](https://www.assemblyai.com/blog/where-voice-agent-stacks-start-showing-their-limits), that's the signal.

## Wrapping up

Most voice agent debugging starts in the wrong place. Something went wrong on a call, and the first instinct is to open the system prompt, because the prompt is the part you wrote.

But the transcriber is the only component whose errors can't be recovered later. A weak LLM response can be fixed with a better prompt, and a robotic voice can be swapped in an afternoon. A misheard account number is gone: nothing downstream can reconstruct what the caller said, and every layer after it works from the wrong input. That's why an entity error rate of 13.25% against 28.71% shows up in your support tickets and not in your latency dashboards. Pick the transcriber first; in Vapi, almost everything else can be swapped later.

## Resources

- [Companion repo: voice-agent-vapi-assemblyai](https://github.com/kelsey-aai/voice-agent-vapi-assemblyai)
- [Vapi: Create assistant API reference](https://docs.vapi.ai/api-reference/assistants/create)

## License

MIT
