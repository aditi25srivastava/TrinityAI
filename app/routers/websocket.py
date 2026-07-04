from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import base64
import struct
from langchain_core.messages import HumanMessage
from app.agents.coordinator import coordinator_graph
import time
from app.services.analytics import log_metric

router = APIRouter()

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to Trinity AI WebSocket")
    
    # Initialize connection state
    user_id = "default_user"
    selected_personality = "Professional"
    context = ""
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # 1. Update State if passed
            if "personality" in payload:
                selected_personality = payload["personality"]
                
            req_start_time = time.time()
            text_input = payload.get("text", "")
            audio_b64_in = payload.get("audio_b64", "")
            image_b64_in = payload.get("image_b64", "")
            context_image_b64_in = payload.get("context_image_b64", "")
            
            if not text_input and not audio_b64_in:
                continue
                
            print(f"Received text: {text_input}, received audio: {bool(audio_b64_in)}, received webcam: {bool(image_b64_in)}, received context_image: {bool(context_image_b64_in)}")
            
            # Prepare message content
            content = []
            if text_input:
                content.append({"type": "text", "text": text_input})
            elif audio_b64_in:
                content.append({"type": "text", "text": "This audio contains my spoken message. Please listen to it, follow any commands I give you, and respond naturally."})
                
            if context_image_b64_in:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{context_image_b64_in}"}
                })

            if image_b64_in:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64_in}"}
                })
                
            if audio_b64_in:
                # Use local Whisper to transcribe the audio robustly
                from app.services.offline_ai import transcribe_audio_offline
                pcm_bytes = base64.b64decode(audio_b64_in)
                
                # Debug dump
                with open("debug_received_audio.wav", "wb") as f:
                    # Quick wav header for debugging only
                    import struct
                    channels = 1
                    sample_rate = payload.get("sample_rate", 16000)
                    bits_per_sample = 16
                    byte_rate = sample_rate * channels * (bits_per_sample // 8)
                    block_align = channels * (bits_per_sample // 8)
                    data_size = len(pcm_bytes)
                    wav_header = struct.pack(
                        '<4sI4s4sIHHIIHH4sI',
                        b'RIFF', 36 + data_size, b'WAVE',
                        b'fmt ', 16, 1, channels, sample_rate,
                        byte_rate, block_align, bits_per_sample,
                        b'data', data_size
                    )
                    f.write(wav_header + pcm_bytes)
                print("DEBUG: Saved received audio to debug_received_audio.wav")
                
                try:
                    transcribed_text = await asyncio.to_thread(transcribe_audio_offline, pcm_bytes)
                    print(f"DEBUG Whisper Transcribed: {transcribed_text}")
                    if transcribed_text.strip():
                        content.append({"type": "text", "text": f"User's spoken message: {transcribed_text}"})
                    else:
                        content.append({"type": "text", "text": "The user tried to speak, but the audio was completely silent or unintelligible."})
                except Exception as e:
                    print(f"Whisper transcription failed: {e}")
                    content.append({"type": "text", "text": "User's spoken message could not be transcribed."})
            
            # 2. Invoke LangGraph
            state = {
                "messages": [HumanMessage(content=content)],
                "selected_personality": selected_personality,
                "user_id": user_id,
                "context": context
            }
            
            try:
                # Add a timeout so it never hangs indefinitely!
                result = await asyncio.wait_for(coordinator_graph.ainvoke(state), timeout=25.0)
                raw_content = result["messages"][-1].content
                if isinstance(raw_content, list):
                    response_text_raw = " ".join([block.get("text", "") for block in raw_content if block.get("type") == "text"])
                else:
                    response_text_raw = str(raw_content)
                    
                # Clean up the JSON if wrapped in markdown blocks
                response_text_raw = response_text_raw.strip()
                if response_text_raw.startswith("```json"):
                    response_text_raw = response_text_raw[7:]
                if response_text_raw.startswith("```"):
                    response_text_raw = response_text_raw[3:]
                if response_text_raw.endswith("```"):
                    response_text_raw = response_text_raw[:-3]
                    
                try:
                    parsed = json.loads(response_text_raw)
                    response_text = parsed.get("response", response_text_raw)
                    emotion = parsed.get("emotion", "neutral")
                    satisfaction_score = parsed.get("satisfaction_score", 5.0)
                    success_rate = parsed.get("success_rate", 0.5)
                except Exception as json_err:
                    print(f"Failed to parse JSON response: {response_text_raw}. Error: {json_err}")
                    response_text = response_text_raw
                    emotion = "neutral"
                    satisfaction_score = 5.0
                    success_rate = 0.5
            except asyncio.TimeoutError:
                print("Error: AI backend timed out taking too long to respond.")
                response_text = "I'm sorry, I took too long to think and timed out."
                emotion = "sad"
                satisfaction_score = 0.0
                success_rate = 0.0
            except Exception as e:
                import traceback
                with open("error_log.txt", "w") as f:
                    traceback.print_exc(file=f)
                print(f"Error parsing graph result: {e}")
                print("--- FALLING BACK TO OFFLINE LOCAL LLM ---")
                try:
                    from app.services.offline_ai import transcribe_audio_offline, query_local_llm
                    # If there's audio, transcribe it locally
                    if audio_b64_in:
                        pcm_bytes = base64.b64decode(audio_b64_in)
                        print("Transcribing audio locally via Whisper...")
                        prompt_text = await asyncio.to_thread(transcribe_audio_offline, pcm_bytes)
                    else:
                        prompt_text = text_input
                    
                    if not prompt_text:
                        prompt_text = "I am offline and didn't hear anything."

                    local_response = await asyncio.to_thread(query_local_llm, prompt_text, selected_personality)
                    response_text = "[OFFLINE MODE - Check Internet] " + local_response.get("response", "I'm offline and thinking.")
                    emotion = local_response.get("emotion", "neutral")
                    
                except Exception as offline_err:
                    import traceback
                    traceback.print_exc()
                    print(f"Total Failure (Offline fallback also failed): {offline_err}")
                    response_text = f"[Offline Fallback Error] I am offline and my local brain is sleeping. Error: {offline_err}"
                    emotion = "sad"
                    satisfaction_score = 0.0
                    success_rate = 0.0

            # 3. Text to Speech / Viseme generation
            audio_b64 = ""
            tts_start_time = time.time()
            try:
                import edge_tts
                import tempfile
                import os
                
                communicate = edge_tts.Communicate(response_text, "en-US-AriaNeural")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_path = fp.name
                await asyncio.wait_for(communicate.save(temp_path), timeout=10.0)
                
                with open(temp_path, "rb") as f:
                    audio_bytes = f.read()
                os.remove(temp_path)
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            except Exception as tts_err:
                print(f"Error generating Edge TTS (probably offline): {tts_err}")
                print("--- FALLING BACK TO OFFLINE LOCAL TTS ---")
                try:
                    from app.services.offline_ai import generate_local_tts
                    audio_b64 = await asyncio.to_thread(generate_local_tts, response_text)
                except Exception as local_tts_err:
                    print(f"Local TTS also failed: {local_tts_err}")
                    
            tts_time_ms = (time.time() - tts_start_time) * 1000
            total_latency_ms = (time.time() - req_start_time) * 1000
            
            # Log metrics
            log_metric(
                latency_ms=total_latency_ms,
                tts_time_ms=tts_time_ms,
                stt_accuracy=0.98 if audio_b64_in else 1.0, # Dummy for now
                satisfaction_score=float(satisfaction_score),
                success_rate=float(success_rate),
                personality=selected_personality
            )

            await websocket.send_json({
                "type": "text",
                "text": response_text,
                "emotion": emotion,
                "visemes": [], # Stub
                "audio_b64": audio_b64 
            })
            
    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Fatal error in websocket: {e}")
        with open("fatal_error.txt", "w") as fef:
            traceback.print_exc(file=fef)
        try:
            await websocket.close()
        except:
            pass

