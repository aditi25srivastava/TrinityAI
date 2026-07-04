import os
import tempfile
import subprocess
import base64
import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from faster_whisper import WhisperModel

# Initialize Whisper model (loaded lazily or globally)
# "tiny" or "base" model is incredibly fast on Mac and very accurate.
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        # device="cpu" is safer on generic Macs, compute_type="int8" uses less memory
        print("Loading local Whisper model for Offline STT...")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

def transcribe_audio_offline(pcm_bytes: bytes) -> str:
    """
    Takes raw 16000Hz 16-bit mono PCM bytes and returns transcribed text.
    """
    import wave
    import struct
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        wav_path = fp.name
        
    try:
        # Save PCM bytes to a proper WAV file so Whisper can read it
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_bytes)
            
        model = get_whisper_model()
        segments, info = model.transcribe(wav_path, beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

def query_local_llm(prompt: str, personality: str) -> dict:
    """
    Queries local Ollama (Gemma) and forces a JSON response format.
    """
    print(f"Querying local LLM (Ollama) with prompt: {prompt}")
    
    system_prompt = f"""You are Trinity, an AI assistant with the following personality: {personality}.
    You are currently running in OFFLINE FALLBACK MODE because the internet is down.
    You MUST respond with a JSON object exactly like this:
    {{
        "response": "Your spoken response here",
        "emotion": "neutral"
    }}
    Emotions can be: neutral, happy, sad, angry, surprised.
    Do NOT include markdown block formatting, just the raw JSON object.
    """
    
    llm = ChatOllama(model="gemma:2b", format="json", temperature=0.7)
    
    messages = [
        HumanMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    try:
        result = llm.invoke(messages)
        # Parse the JSON
        try:
            parsed = json.loads(result.content)
            return parsed
        except json.JSONDecodeError:
            return {"response": result.content, "emotion": "neutral"}
    except Exception as e:
        print(f"Ollama Error: {e}")
        return {"response": "I'm sorry, my local brain is having trouble thinking.", "emotion": "sad"}

def generate_local_tts(text: str) -> str:
    """
    Uses macOS 'say' command to generate TTS completely offline.
    Returns base64 encoded WAV string.
    """
    print("Generating local TTS using macOS 'say'...")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
        temp_path = fp.name
        
    try:
        # Run macOS 'say'. -v Samantha is a high quality default voice.
        # --data-format=LEF32@16000 ensures it exports to a WAV format compatible with Unity
        subprocess.run([
            "say", 
            "-v", "Samantha", 
            "-o", temp_path, 
            "--data-format=LEF32@16000", 
            text
        ], check=True)
        
        with open(temp_path, "rb") as f:
            wav_bytes = f.read()
            
        return base64.b64encode(wav_bytes).decode('utf-8')
    except Exception as e:
        print(f"Offline TTS Error: {e}")
        return ""
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
