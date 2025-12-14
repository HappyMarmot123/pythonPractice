import tkinter as tk
import time

running = False
start_time = 0
elapsed_time = 0

def update_time_label():
    global elapsed_time, running
    
    if running:
        elapsed_time = time.time() - start_time
        
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time - int(elapsed_time)) * 10)
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds}"
        
        time_label.config(text=time_str)
        
        time_label.after(100, update_time_label)

def start_stopwatch():
    global running, start_time, elapsed_time
    
    if not running:
        running = True
        start_time = time.time() - elapsed_time
        
        start_button.config(text="중지", command=stop_stopwatch, bg="orange")
        reset_button.config(state=tk.DISABLED)
        
        update_time_label()
    else:
        pass

def stop_stopwatch():
    global running
    
    if running:
        running = False
        start_button.config(text="재개", command=start_stopwatch, bg="green")
        reset_button.config(state=tk.NORMAL)

def reset_stopwatch():
    global running, start_time, elapsed_time
    
    if not running:
        elapsed_time = 0
        time_label.config(text="00:00:00.0")
        start_button.config(text="시작", command=start_stopwatch, bg="green")
        reset_button.config(state=tk.DISABLED)

root = tk.Tk()
root.title("미니 스톱워치")

time_label = tk.Label(root, text="00:00:00.0", font=("Helvetica", 48), padx=20, pady=20)
time_label.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="시작", command=start_stopwatch, font=("Helvetica", 14), width=8, bg="green", fg="white")
start_button.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(button_frame, text="초기화", command=reset_stopwatch, font=("Helvetica", 14), width=8, state=tk.DISABLED)
reset_button.pack(side=tk.LEFT, padx=10)

root.mainloop()