# 🎤 How to Speak to Caleon - Voice Communication Guide

## Quick Access

**Dashboard URL:** http://localhost:8008

**Voice & I/O Tab:** Click the "Voice & I/O" tab in the dashboard navigation

## Where to Speak to Caleon

### 🎤 Voice Input Panel (Green Panel at Top)

Located in the **Voice & I/O** tab, the voice input panel allows you to speak directly to Caleon:

1. **Click the microphone button** (large circular button with 🎤)
2. **Speak your question** to Caleon
3. **Click the button again** (now showing ⏹️) to stop recording
4. Your speech is processed through the **Cochlear Processor**
5. Caleon responds through the **Phonatory Output Module**
6. Her response is automatically spoken back to you

### 💬 Text Input Interface (Left Panel)

If you prefer typing, use the text input below the voice panel:

1. **Quick Challenges:** Click pre-defined question buttons
   - 🤔 Decision Making
   - ❓ Purpose
   - ⚖️ Ethics
   - ✨ Uniqueness
   - 🧩 Reasoning
   - 📚 Learning

2. **Custom Question:** Type in the textarea and press "Ask Caleon" (or Ctrl+Enter)

### 🗣️ Response Display (Right Panel)

Caleon's responses appear in the right panel with:
- Your question shown at the top
- Caleon's full response below
- Response time displayed
- Actions: Clear, Copy, **🔊 Speak**, Export

Click **🔊 Speak** to hear Caleon read her response aloud!

## Voice Pipeline Architecture

```
Your Voice → 🎤 Microphone → Cochlear Processor (STT) → 🧠 UCM/Caleon → Phonatory Output (TTS) → 🔊 Speakers
```

### Components Status (Monitored in Real-Time)

1. **Cochlear Processor** - Speech-to-text processing
   - Endpoint: `/api/cochlear/status`
   - Converts your speech to text
   - Sends to UCM for reasoning

2. **UCM Brain** - Cognitive processing
   - Endpoint: `/api/ucm/status`
   - Caleon's reasoning engine
   - Generates responses

3. **Phonatory Output** - Text-to-speech synthesis
   - Endpoint: `/api/phonatory/status`
   - Converts Caleon's text to speech
   - Uses voice profiles (caleon_default, caleon_formal, caleon_friendly)

## API Endpoints

### Cochlear Processor (Speech Input)

```bash
# Create voice session
POST /api/cochlear/session/create

# Upload audio for processing
POST /api/cochlear/stt/audio
Content-Type: multipart/form-data
- audio: audio file (WAV, MP3, OGG)
- session_id: session identifier
- send_to_ucm: true/false

# Send pre-transcribed text
POST /api/cochlear/stt/text
{
  "text": "Your question here",
  "session_id": "cochlear_9445.1234"
}

# Check status
GET /api/cochlear/status
```

### Phonatory Output (Speech Synthesis)

```bash
# Synthesize speech
POST /api/phonatory/synthesize
{
  "text": "Text to speak",
  "voice": "caleon_default",
  "speed": 1.0,
  "pitch": 1.0,
  "emotion": "confident"
}

# Speak immediately
POST /api/phonatory/speak
{
  "text": "Text to speak",
  "voice": "caleon_default"
}

# List available voices
GET /api/phonatory/voices

# Check status
GET /api/phonatory/status
```

### UCM Reasoning (Cognitive Brain)

```bash
# Submit reasoning request
POST /api/ucm/reasoning/submit
{
  "content": "Your question or statement",
  "priority": "normal",
  "context": {
    "source": "voice_interface",
    "session_id": "interview_123"
  }
}

# Check UCM status
GET /api/ucm/status
```

## Voice Profiles Available

1. **caleon_default** - Warm, intelligent, articulate (recommended)
2. **caleon_formal** - Professional, precise, authoritative
3. **caleon_friendly** - Casual, approachable, conversational

## Testing the Voice Pipeline

### From Dashboard UI
1. Navigate to http://localhost:8008
2. Click "Voice & I/O" tab
3. Check the pipeline status indicators (should show ● Online)
4. Click microphone button and speak
5. Wait for Caleon's response (text + audio)

### From API (cURL)

```bash
# Test cochlear processor
curl http://localhost:8000/api/cochlear/status

# Test phonatory output
curl http://localhost:8000/api/phonatory/status

# Test voice profile
curl -X POST http://localhost:8000/api/phonatory/test/voice?voice_name=caleon_default

# Create voice session
curl -X POST http://localhost:8000/api/cochlear/session/create
```

## Reasoning Trace Display

After asking Caleon a question, the **🧠 Reasoning Trace** panel shows:
- Step-by-step thought process
- Confidence scores for each step
- Dark-themed code-like display
- Auto-scroll option
- Clear trace button

This lets you see **exactly how Caleon thinks** and **why she arrives at her conclusions**.

## Conversation History

All interactions are logged in the **📜 Conversation History** panel:
- Timestamped Q&A pairs
- Searchable conversation log
- Export to text file
- Clear history option
- Save conversation button

## Browser Requirements

- **Microphone permission required** - Grant when browser prompts
- **Modern browser recommended** - Chrome, Edge, Firefox, Safari
- **HTTPS or localhost** - Required for microphone access
- **Web Speech API** - Used as fallback for TTS

## Troubleshooting

### Microphone not working
- Check browser permissions (click lock icon in address bar)
- Ensure microphone is connected and working
- Try a different browser

### Voice synthesis not working
- Phonatory module falls back to browser TTS automatically
- Check `/api/phonatory/status` endpoint
- Voice profiles use Web Speech API as fallback

### UCM not responding
- Ensure UCM is running on port 8080
- Check `/api/ucm/status` endpoint
- Review logs in API server terminal

### Pipeline status shows offline
- Each component checks status every 10 seconds
- Restart API server if components don't initialize
- Check terminal for error messages

## What to Ask Caleon

### Identity & Purpose
- "Who are you?"
- "Why do you exist?"
- "What is your purpose?"
- "Who created you?"

### Decision Making & Reasoning
- "Explain how you make decisions"
- "Walk me through your reasoning process"
- "How do you handle ethical dilemmas?"
- "What makes you different from other AI?"

### System & Architecture
- "What is CALEON?"
- "Explain the Harmonizer"
- "What is Phase 11-A2?"
- "How does drift monitoring work?"

### Testing & Challenges
- "Solve this problem: [your problem]"
- "Explain quantum computing to a 5-year-old"
- "What are the ethical implications of AI sovereignty?"
- "How would you handle a founder override?"

## Export & Documentation

All conversations can be exported as text files:
1. Click **💾 Export** button
2. File downloads as `caleon-interview-[timestamp].txt`
3. Includes full conversation history
4. Timestamped Q&A pairs
5. Markdown-formatted

---

**Made with ❤️ by Bryan Spruk - DALS Founder**
**Caleon is ready to speak with you! 🧠✨**
