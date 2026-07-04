import struct
import base64

# Generate 1 second of 16000Hz 16-bit mono PCM silence
pcm_bytes = b'\x00' * (16000 * 2)

channels = 1
sample_rate = 16000
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
wav_bytes = wav_header + pcm_bytes

with open("test_silence.wav", "wb") as f:
    f.write(wav_bytes)
print("WAV saved to test_silence.wav")
