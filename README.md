# Vapi voice agent with AssemblyAI Universal-3.6 Pro Realtime

Use **AssemblyAI Universal-3.6 Pro Realtime** as the speech-to-text engine inside your Vapi voice agent — and get semantic turn detection, keyterm prompting, and a 307 ms median time to final transcript (on Pipecat's open benchmark) inside Vapi's managed voice platform.

## What is Vapi?

Vapi handles telephony, turn-taking, and orchestration so you don't have to. It supports 14+ speech-to-text providers. You bring your AssemblyAI key, Vapi handles the rest.

## Why Universal-3.6 Pro Realtime?

On [AssemblyAI's English voice-agent benchmark](https://www.assemblyai.com/blog/universal-3-6-pro-realtime-research) (12,460 scripted voice-agent scenarios):

| Metric | Universal-3.6 Pro Realtime | Deepgram Flux EN | ElevenLabs Scribe v2 | Deepgram Nova-3 |
|--------|----------------------------|------------------|----------------------|-----------------|
| Word error rate | 5.19% | 13.50% | 7.78% | 8.64% |
| Entity error rate | 14.4% | 30.1% | 18.5% | 26.1% |
| Names | 10.9% | 29.0% | 14.8% | 24.3% |
| Codes / IDs | 10.0% | 46.1% | 12.0% | 27.6% |
| Phone numbers | 2.4% | 11.5% | 3.4% | 4.5% |

On [Pipecat's open STT benchmark](https://github.com/pipecat-ai/stt-benchmark) it posts a 0.96% pooled semantic word error rate.

## Setup: add AssemblyAI to Vapi

### Step 1 — Add your API key

1. Go to [dashboard.vapi.ai](https://dashboard.vapi.ai)
2. Navigate to **Settings > Transcriber Providers**
3. Add your AssemblyAI API key

### Step 2 — Create an assistant (dashboard)

1. Click **Create Assistant**
2. Under **Transcriber**, select **Assembly AI**
3. Under **Model**, select **universal-3-6-pro** (Universal-3.6 Pro Realtime)
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
    "speechModel": "universal-3-6-pro",
    "language": "en",
    "keytermsPrompt": ["YourBrand", "SpecialTerm"],
    "confidenceThreshold": 0.4
  }
}
```

Only `provider` and `speechModel` are required. `language` accepts only `en` or `multi` — pass `languageCodes` instead for any other language. `confidenceThreshold` is the Vapi-side floor below which a transcript fragment is discarded rather than passed to your LLM.

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

This is the single biggest accuracy lever you have inside Vapi, and it's included in the base rate. Boost recognition for domain-specific vocabulary that a general speech model would otherwise miss:

```json
{
  "transcriber": {
    "provider": "assembly-ai",
    "speechModel": "universal-3-6-pro",
    "language": "en",
    "keytermsPrompt": [
      "hemoglobin A1c",
      "Jardiance",
      "deductible",
      "prior authorization"
    ]
  }
}
```

Up to 100 keyterms, each up to 50 characters. Changes take effect on the next call — no assistant restart, no redeploy. Spend the slots on terms a general-purpose model has never seen in your context (SKUs, clinician names, internal system names), not common English words.

## Supported languages

Universal-3.6 Pro Realtime covers 32 languages with automatic language detection and native mid-sentence code-switching (including Hinglish): English, Spanish, French, German, Italian, Portuguese, Arabic, Danish, Dutch, Hebrew, Hindi, Japanese, Mandarin, Vietnamese, Finnish, Norwegian, Swedish, Turkish, Afrikaans, Cantonese, Catalan, Estonian, Galician, Korean, Marathi, Norwegian Nynorsk, Persian, Romanian, Russian, Urdu, Xhosa, and Zulu.

If you know the language in advance, pin it:

```json
{
  "transcriber": {
    "provider": "assembly-ai",
    "speechModel": "universal-3-6-pro",
    "languageCodes": ["es"]
  }
}
```

Leave `languageCodes` off when your line genuinely takes calls in more than one language.

## Migrating from `u3-rt-pro` or `universal-3-5-pro`

Change the key and the value: `"model": "u3-rt-pro"` becomes `"speechModel": "universal-3-6-pro"` in your assistant's transcriber block (or pick it in the dashboard's Model dropdown). Keyterms, language codes, and confidence thresholds carry over unchanged. `universal-3-5-pro` stays available if you need to pin the previous model.

## When to choose AssemblyAI over Deepgram in Vapi

| What you're optimizing for | Pick | Why |
|----------------------------|------|-----|
| Accuracy on voice-agent audio | AssemblyAI | 5.19% WER vs Deepgram Flux EN's 13.50% on AssemblyAI's English voice-agent benchmark |
| Account numbers, emails, spelled-out IDs | AssemblyAI | 14.4% entity error rate vs 30.1%; phone numbers 2.4% vs 11.5% |
| Names and codes / IDs | AssemblyAI | Names 10.9% vs 29.0%, codes / IDs 10.0% vs 46.1% |
| Medical or clinical terminology | AssemblyAI | Keyterm prompting included in the base rate, plus Medical Mode |
| Turn-taking that isn't just silence timing | AssemblyAI | End-of-turn detection combines semantic context with voice activity; final transcript a median 307 ms after the speaker stops (Pipecat) |
| Multilingual callers | AssemblyAI | 32 languages, native mid-sentence code-switching |
| A language outside those 32 | Worth comparing | Our 99+ language coverage lives on Universal-2 for pre-recorded audio, not the Pro realtime line |

## Pricing

Universal-3.6 Pro Realtime is $0.45/hr base, billed on session duration, with no minimum and no concurrency cap. Keyterm prompting is included. Vapi's platform fee and your LLM and TTS providers bill separately. See [assemblyai.com/pricing](https://www.assemblyai.com/pricing).

## Resources

- [Vapi AssemblyAI provider docs](https://docs.vapi.ai/providers/transcriber/assembly-ai)
- [Vapi API reference](https://docs.vapi.ai/api-reference)
- [AssemblyAI docs](https://www.assemblyai.com/docs)
- [Universal-3.6 Pro Realtime release notes](https://www.assemblyai.com/blog/universal-3-6-pro-realtime)
- [Vapi vs Pipecat vs LiveKit](https://www.assemblyai.com/blog/vapi-vs-pipecat-vs-livekit)

---

<div class="blog-cta_component">
  <div class="blog-cta_title">Switch your Vapi agent to AssemblyAI</div>
  <div class="blog-cta_rt w-richtext">
    <p>Sign up for a free AssemblyAI account, add your key to Vapi's dashboard, and enable Universal-3.6 Pro Realtime in minutes.</p>
  </div>
  <a href="https://www.assemblyai.com/dashboard/signup" class="button w-button">Start building</a>
</div>

<div class="blog-cta_component">
  <div class="blog-cta_title">Experiment with real-time turn detection</div>
  <div class="blog-cta_rt w-richtext">
    <p>Try streaming transcription in our Playground and observe how semantic end-of-turn detection shapes turn boundaries in real time. See how Universal-3.6 Pro Realtime handles partials, finals, and entities on your own audio.</p>
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
