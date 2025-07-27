# 🔐 Advanced SSH Brute Force Tool with GUI

A powerful and customizable Python-based SSH brute-force tool with an intuitive GUI built using Tkinter. This tool supports multi-threading, delay/retry control, real-time logging, and color-coded output highlighting. Designed for cybersecurity research and educational penetration testing.

---

## 📌 Features

- GUI interface for easier operation (start/stop with input fields).
- Multi-threaded brute-force attacks.
- Retry mechanism for unstable connections.
- Password generation mode (optional).
- Color-coded live console output.
- Result logging and failed attempt saving.

---

## 🖥 GUI Preview

> Simple and clean interface powered by Tkinter  
> Start and stop buttons, file pickers, and real-time output view.

<img width="1267" height="1001" alt="Image" src="https://github.com/user-attachments/assets/e0b17b52-7dcb-4b80-a10e-84e63eb6fa79" />

---

## ⚙ Requirements

Ensure you have Python 3.7+ installed.

Install dependencies:

bash
pip install paramiko colorama

## 🚀 How to Use

### 🔧 Command-line Mode:

bash
python advance_ssh_brute.py <target-ip> -U userlist.txt -P passlist.txt --threads 4 --delay 1 --max-user-retries 5 --output results.txt

### 🖱 GUI Mode:

bash
python ssh_gui.py

## 📂 Folder Structure

<pre>
  ├── advance_ssh_brute.py   # CLI Brute force logic 
  ├── ssh_gui.py             # GUI wrapper 
  ├── userlist.txt           # List of usernames 
  ├── passlist.txt           # List of passwords 
  ├── results.txt            # Output file 
  ├── failed_attempts.txt    # Failed credentials 
  ├── requirements.txt       # Python dependencies 
  └── README.md              # You're here!  </pre>


## ✅ Output Example

text
[+] Found: testuser@192.168.1.10:admin123
[-] Invalid: root:root123
[!] SSH Retry (1) for admin:password123

Results saved to results.txt and brute_log_TIMESTAMP.txt


## 📚 Applications

- Educational penetration testing  
- Security awareness training  
- Brute-force defense evaluation  
- Custom testing of SSH login resilience  

## ⚠ Disclaimer

This tool is for educational and authorized testing purposes only.  
*Do not use it against systems without explicit written permission.*  
The developer is not responsible for any misuse.


## 🙏 Thank You

If you like this project, please ⭐ the repo!



# License

This project is open-source and free to use by anyone for personal or educational purposes.  
Feel free to modify, distribute, and use the code as long as proper credit is given to the original author, *Saini Harshith*.
