import tkinter as tk
import pyaudio
import wave
import threading
import os
import subprocess
import json

FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK = 1024
RATE = 16000
WAVE_OUTPUT_FILENAME = ""

is_recording = False

def record_audio():
    global is_recording
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    status_label.config(text="Đang ghi âm...")
    is_recording = True
    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    selected_emotion = emotion_var.get()
    selected_question = f"Câu {question_var.get() + 1}" if question_var.get() >= 0 else "NoQuestion"
    user_name = name_entry.get().strip()

    output_dir = os.path.join("Audio", f"{selected_emotion}")
    os.makedirs(output_dir, exist_ok=True)

    WAVE_OUTPUT_FILENAME = os.path.join(output_dir, f"{selected_emotion}_{selected_question}_{user_name}.wav")

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    status_label.config(text="Hoàn tất ghi âm!")

def start_recording():
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

def stop_recording():
    global is_recording
    is_recording = False
    status_label.config(text="Ghi âm đã dừng!")

def open_audio_folder():
    selected_emotion = emotion_var.get()
    output_dir = os.path.join("Audio", f"{selected_emotion}")
    if os.path.exists(output_dir):
        subprocess.Popen(f'explorer "{output_dir}"')
    else:
        status_label.config(text="Thư mục không tồn tại!")

def load_content_data():
    with open('content.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def update_content_label():
    selected_emotion = emotion_var.get()
    selected_question = question_var.get() 
    
    if selected_question >= 0:
        if selected_emotion in content_data:
            # Kiểm tra xem chỉ số câu hỏi có hợp lệ không
            if selected_question < len(content_data[selected_emotion]):
                content = content_data[selected_emotion][selected_question]
                content_label.config(text='Nội dung: ' + content)
            else:
                content_label.config(text="Nội dung không có sẵn cho câu hỏi này.")
        else:
            content_label.config(text="Nội dung không có sẵn cho cảm xúc này.")
    else:
        content_label.config(text="")

root = tk.Tk()
root.title("Voice Recorder")
root.geometry("900x740")

title_label = tk.Label(root, text="Ứng Dụng Ghi Âm", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

record_icon = tk.PhotoImage(file=r"Icon\play-button.png")
record_icon = record_icon.subsample(6, 6)
record_button = tk.Button(root, image=record_icon, borderwidth=0)
record_button.pack(pady=20)

status_frame = tk.Frame(root)
status_frame.pack(pady=10)

status_label = tk.Label(status_frame, text="", font=("Arial", 12))
status_label.pack(side=tk.LEFT, padx=5)

emotion_var = tk.StringVar(value="Thân Thiện")
emotion_frame = tk.Frame(status_frame)
emotion_frame.pack(side=tk.LEFT, padx=5)

content_data = load_content_data()

emotions = ["Thân Thiện", "Vui Vẻ", "Mệt Mỏi", "Cáu Giận", "Lạnh Lùng"]
for emotion in emotions:
    tk.Radiobutton(emotion_frame, text=emotion, variable=emotion_var, value=emotion).pack(anchor=tk.W)

question_var = tk.IntVar(value=-1) 
question_frame = tk.Frame(status_frame)
question_frame.pack(side=tk.LEFT, padx=5)

for i in range(12):
    tk.Radiobutton(question_frame, text=f"Câu {i + 1}", variable=question_var, value=i).pack(anchor=tk.W)

name_label = tk.Label(root, text="Nhập tên người ghi âm:", font=("Arial", 12))
name_label.pack(pady=5)

name_entry = tk.Entry(root, font=("Arial", 12))
name_entry.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Bắt đầu", command=start_recording, width=15, height=2)
start_button.pack(side=tk.LEFT, padx=5, pady=5)
start_button.bind("<Enter>", lambda e: start_button.config(cursor="hand2"))
start_button.bind("<Leave>", lambda e: start_button.config(cursor=""))

stop_button = tk.Button(button_frame, text="Kết thúc ghi âm", command=stop_recording, width=15, height=2)
stop_button.pack(side=tk.LEFT, padx=5, pady=5)
stop_button.bind("<Enter>", lambda e: stop_button.config(cursor="hand2"))
stop_button.bind("<Leave>", lambda e: stop_button.config(cursor=""))

check_button = tk.Button(button_frame, text="Kiểm tra file vừa ghi", command=open_audio_folder, width=20, height=2)
check_button.pack(side=tk.LEFT, padx=5, pady=5)
check_button.bind("<Enter>", lambda e: check_button.config(cursor="hand2"))
check_button.bind("<Leave>", lambda e: check_button.config(cursor=""))

status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=10)

content_label = tk.Label(root, text="", font=("Arial", 12), justify=tk.LEFT)
content_label.pack(pady=10)

question_var.trace("w", lambda *args: update_content_label())  
emotion_var.trace("w", lambda *args: update_content_label())  

root.mainloop()
