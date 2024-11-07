import pyaudio
import wave
import numpy as np
import noisereduce as nr
import matplotlib.pyplot as plt
from pydub import AudioSegment

FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 2.5
CHUNK = 1024
RATE = 24414 
WAVE_OUTPUT_FILENAME = "output_normal.wav"

p = pyaudio.PyAudio()

# Bắt đầu ghi âm
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK) 

print("*Recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data) 

print("*Done recording")

stream.stop_stream()
stream.close()
p.terminate()

# Lưu dữ liệu ghi âm vào file WAV
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# Chuyển đổi dữ liệu ghi âm thành mảng numpy để xử lý
audio_data = b''.join(frames)
audio_np = np.frombuffer(audio_data, dtype=np.int16)

# Giảm nhiễu sử dụng thư viện noisereduce
reduced_noise = nr.reduce_noise(y=audio_np, sr=RATE, prop_decrease=0.6) 

# Vẽ đồ thị tín hiệu gốc và tín hiệu giảm nhiễu
fig, ax = plt.subplots(2, 1, figsize=(15, 8))
ax[0].set_title("Original Signal")
ax[0].plot(audio_np)
ax[1].set_title("Reduced Noise Signal")
ax[1].plot(reduced_noise)
plt.show()

# Chuyển tín hiệu giảm nhiễu thành file audio
reduced_audio = AudioSegment(
    reduced_noise.tobytes(),
    frame_rate=RATE,
    sample_width=audio_np.itemsize,  # Kích thước mẫu của âm thanh
    channels=CHANNELS
)

# Lưu tín hiệu giảm nhiễu vào file WAV
reduced_audio.export("output_reduced_noise.wav", format="wav")

print("Reduced noise audio saved as 'output_reduced_noise.wav'")
