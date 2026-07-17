# Vapi voice agent with AssemblyAI Universal-3.5 Pro Realtime

Use **AssemblyAI Universal-3.5 Pro Realtime** as the speech-to-text engine inside your Vapi voice agent — and get punctuation-based turn detection, keyterm prompting, and ~150 ms P50 latency (6.99% WER on Pipecat's open benchmark) inside Vapi's managed voice platform.

## What is Vapi?

Vapi handles telephony, turn-taking, and orchestration so you don't have to. It supports 14+ speech-to-text providers. You bring your AssemblyAI key, Vapi handles the rest.

## Setup: add AssemblyAI to Vapi

### Step 1 — Add your API key

1. Go to [dashboard.vapi.ai](https://dashboard.vapi.ai)
2. Navigate to **Settings > Transcriber Providers**
3. Add your AssemblyAI API key

### Step 2 — Create an assistant (dashboard)

1. Click **Create Assistant**
2. Under **Transcriber**, select **Assembly AI**
3. Under **Model**, select **universal-3-5-pro** (Universal-3.5 Pro Realtime)
4. Save and test via the web call button

### Step 3 — Create an assistant (API)

```bash
python create_assistant.py create
```

This creates a fully configured assistant:

```json
{
  "transcriber": {
    "provider": "assembly-ai",
    "model": "universal-3-5-pro",
    "language": "en",
    "keytermsPrompt": ["YourBrand", "SpecialTerm"],
    "confidenceThreshold": 0.4
  }
}
```

## Quick start

```bash
git clone https://github.com/kelsey-aai/voice-agent-vapi-assemblyai
cd voice-agent-vapi-assemblyai

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys

# Create an assistant
python create_assistant.py create

# Make an outbound test call (requires Twilio number in .env)
python create_assistant.py call --assistant-id <id> --phone +1XXXXXXXXXX

# Start the webhook server
uvicorn webhook_server:app --port 8000
```

## Keyterm prompting

This is one of the biggest accuracy levers available in Vapi. Boost recognition for domain-specific vocabulary that a general speech model would otherwise miss:

```python
"keytermsPrompt": [
    "hemoglobin A1c",     # medical
    "HIPAA",              # compliance
    "Jardiance",          # drug name
    "deductible",         # insurance
]
```

Up to 100 keyterms, each up to 50 characters. Takes effect immediately on the next call — no assistant restart needed.

## Supported languages

Universal-3.5 Pro Realtime supports 18 languages — including English, Spanish, French, German, Italian, and Portuguese — with native mid-sentence code-switching:

```json
{ "transcriber": { "provider": "assembly-ai", "model": "universal-3-5-pro", "language": "es" } }
```

## When to choose AssemblyAI over Deepgram in Vapi

| Use case | Recommended |
|----------|-------------|
| Accuracy on real agent conversations | AssemblyAI Universal-3.5 Pro Realtime (6.99% WER on Pipecat's open benchmark) |
| Low-latency streaming transcripts | AssemblyAI (~150 ms P50, partial + final) |
| Account numbers, serial codes, emails | AssemblyAI (strong entity accuracy) |
| Medical or clinical terminology | AssemblyAI (included keyterm prompting) |
| Sharper answers to the agent's questions | AssemblyAI (Context Carryover) |
| Multilingual callers | AssemblyAI (18 languages, native code-switching) |

## Related tutorials

- [Tutorial 04: Twilio + Universal-3 Pro Streaming](../04-twilio-universal-3-pro) — build a custom phone agent with full control over the audio pipeline
- [Tutorial 07: Retell + AssemblyAI](../07-retell-assemblyai) — another managed voice platform, with AssemblyAI post-call analytics
- [Tutorial 01: LiveKit + Universal-3 Pro Streaming](../01-livekit-universal-3-pro) — for WebRTC-based agents with more infrastructure control

## Resources

- [AssemblyAI Vapi integration](https://www.assemblyai.com/docs/universal-streaming/voice-agents/vapi)
- [Vapi AssemblyAI provider docs](https://docs.vapi.ai/providers/transcriber/assembly-ai)
- [Vapi API reference](https://docs.vapi.ai/api-reference)

---

<div class="blog-cta_component">
  <div class="blog-cta_title">Switch your Vapi agent to AssemblyAI</div>
  <div class="blog-cta_rt w-richtext">
    <p>Sign up for a free AssemblyAI account, add your key to Vapi's dashboard, and enable Universal-3.5 Pro Realtime in minutes.</p>
  </div>
  <a href="https://www.assemblyai.com/dashboard/signup" class="button w-button">Start building</a>
</div>

<div class="blog-cta_component">
  <div class="blog-cta_title">Experiment with real-time turn detection</div>
  <div class="blog-cta_rt w-richtext">
    <p>Try streaming transcription in our Playground and observe how punctuation and silence handling shape turn boundaries in real time. Compare behaviors across Universal-3.5 Pro Realtime and Universal-streaming models.</p>
  </div>
  <a href="https://www.assemblyai.com/playground" class="button w-button">Open playground</a>
</div>

<div class="blog-cta_component">
  <div class="blog-cta_title">Scale voice AI across your call operations</div>
  <div class="blog-cta_rt w-richtext">
    <p>Discuss volume pricing, enterprise SLAs, and custom integration support with our team. We work directly with teams deploying voice agents at scale.</p>
  </div>
  <a href="https://www.assemblyai.com/contact" class="button w-button">Talk to an AI expert</a>
</div>
