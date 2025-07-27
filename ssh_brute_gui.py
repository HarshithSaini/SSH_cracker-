import tkinter as tk
from tkinter import filedialog, scrolledtext
from threading import Thread
from subprocess import Popen, PIPE, STDOUT
from PIL import Image, ImageTk
import os
import sys

process_ref = None

def browse_file(var):
    filename = filedialog.askopenfilename()
    if filename:
        var.set(filename)

def run_bruteforce():
    output_area.delete(1.0, tk.END)
    host = host_var.get().strip()
    userlist = user_file_path.get().strip()
    passlist = pass_file_path.get().strip()
    threads = thread_count.get()
    delay_val = delay.get()
    max_user = max_retries.get()
    output = output_file_path.get().strip()

    if not (host and userlist and passlist):
        output_area.insert(tk.END, "❌ Error: Please fill all required fields.\n", "error")
        return

    # Use full path for output if needed
    if not os.path.isabs(output):
        output = os.path.join(os.getcwd(), output)

    # Prepare the command
    script_path = os.path.join(os.getcwd(), "advance_ssh_brute.py")
    if not os.path.exists(script_path):
        output_area.insert(tk.END, f"❌ Error: Script not found at {script_path}\n", "error")
        return

    cmd = [
        sys.executable,
        "-u",  # Unbuffered output
        script_path,
        host,
        "-U", userlist,
        "-P", passlist,
        "--threads", str(threads),
        "--delay", str(delay_val),
        "--max-user-retries", str(max_user),
        "--output", output
    ]

    print("Running command:", " ".join(cmd))  # Optional for debug

    def read_output():
        global process_ref
        try:
            process_ref = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
            if process_ref.stdout is None:
                output_area.insert(tk.END, "❌ Error: Failed to capture process output.\n", "error")
                process_ref = None
                return
            for line in process_ref.stdout:
                tag = "normal"
                if "[+]" in line or "✅" in line:
                    tag = "success"
                elif "[-]" in line or "Invalid" in line:
                    tag = "fail"
                elif "[!]" in line or "retry" in line.lower():
                    tag = "warn"
                elif "❌" in line or "⛔" in line or "Error" in line:
                    tag = "error"

                output_area.insert(tk.END, line, tag)
                output_area.see(tk.END)

            process_ref.wait()
            output_area.insert(tk.END, "\n✅ Brute force finished.\n", "success")
            process_ref = None
        except Exception as e:
            output_area.insert(tk.END, f"❌ Error running script: {e}\n", "error")
            process_ref = None

    Thread(target=read_output).start()

def stop_bruteforce():
    global process_ref
    if process_ref:
        process_ref.terminate()
        output_area.insert(tk.END, "\n⛔ Brute force manually stopped.\n", "warn")
        process_ref = None

# GUI setup
root = tk.Tk()
root.title("SSH Brute Force GUI")
root.geometry("900x700")
root.resizable(False, False)

# Load background image if exists
bg_image_path = "ssh_background.jpg"
if os.path.exists(bg_image_path):
    bg_image = Image.open(bg_image_path).resize((900, 700), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
else:
    root.config(bg="#1e1e1e")

# Variables
host_var = tk.StringVar()
user_file_path = tk.StringVar()
pass_file_path = tk.StringVar()
output_file_path = tk.StringVar(value="results.txt")
thread_count = tk.IntVar(value=4)
max_retries = tk.IntVar(value=99)
delay = tk.DoubleVar(value=1)

# Input container frame
input_container = tk.Frame(root, bg="#000000", bd=2)
input_container.place(relx=0.5, y=30, anchor="n")

def add_label_entry(parent, text, var, width=45):
    tk.Label(parent, text=text, fg="white", bg="#000000", font=("Segoe UI", 10)).pack(pady=(5, 0))
    tk.Entry(parent, textvariable=var, width=width, bg="#1e1e1e", fg="white", insertbackground='white').pack(pady=(0, 5))

# Input fields
add_label_entry(input_container, "Target Host:", host_var)
add_label_entry(input_container, "User List File:", user_file_path)
tk.Button(input_container, text="Browse", command=lambda: browse_file(user_file_path),
          bg="#333333", fg="white").pack()

add_label_entry(input_container, "Password List File:", pass_file_path)
tk.Button(input_container, text="Browse", command=lambda: browse_file(pass_file_path),
          bg="#333333", fg="white").pack()

add_label_entry(input_container, "Threads:", thread_count)
add_label_entry(input_container, "Delay (s):", delay)
add_label_entry(input_container, "Max Retries/User:", max_retries)
add_label_entry(input_container, "Output File:", output_file_path)

# Buttons Frame
btn_frame = tk.Frame(root, bg="#000000")
btn_frame.place(relx=0.5, y=420, anchor="n")

tk.Button(btn_frame, text="▶ Start Brute Force", bg="#1e90ff", fg="white",
          command=run_bruteforce, font=("Segoe UI", 10, "bold"), width=20).pack(side=tk.LEFT, padx=15)

tk.Button(btn_frame, text="■ Stop", bg="#e60000", fg="white",
          command=stop_bruteforce, font=("Segoe UI", 10, "bold"), width=10).pack(side=tk.LEFT)

# Output Area
output_frame = tk.Frame(root)
output_frame.place(x=20, y=480, width=860, height=200)

output_area = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, bg="black", fg="#d4d4d4",
                                        font=("Consolas", 10))
output_area.pack(fill=tk.BOTH, expand=True)

# Color tags
output_area.tag_config("success", foreground="green")
output_area.tag_config("fail", foreground="red")
output_area.tag_config("warn", foreground="yellow")
output_area.tag_config("error", foreground="orange")
output_area.tag_config("normal", foreground="#d4d4d4")

root.mainloop()
