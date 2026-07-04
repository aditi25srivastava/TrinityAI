import sys
import os

def main():
    try:
        from app.services.offline_ai import transcribe_audio_offline
        with open("debug_received_audio.wav", "rb") as f:
            wav_bytes = f.read()
        
        # In websocket.py we pass the raw PCM without header to transcribe_audio_offline
        # But wait, debug_received_audio.wav HAS a wav header (44 bytes).
        # We should strip the first 44 bytes to get the raw PCM!
        pcm_bytes = wav_bytes[44:]
        
        print("Transcribing...")
        text = transcribe_audio_offline(pcm_bytes)
        print(f"User said: {text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
