import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
import sys
import random

os.environ['DISPLAY'] = ':0'

# コマンドライン引数から pi_idx を取得する
if len(sys.argv) > 1:
    try:
        pi_idx = int(sys.argv[1])  # 引数を整数に変換
    except ValueError:
        raise ValueError("pi_idx should be int。")
else:
    raise ValueError("no pi_idx specified")

run_counter = 0
max_runs = 3  # このスクリプトが再起動するまでの最大実行回数

def get_newest_file(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
    for file in files:
        if file.lower().endswith(('.txt', '.log', '.csv')):
            return os.path.join(path, file)
    return None

def get_random_file(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    text_files = [f for f in files if f.lower().endswith(('.txt', '.log', '.csv'))]
    if text_files:
        return os.path.join(path, random.choice(text_files))
    return None

# 他の sync_text.py インスタンスを終了させる関数
def kill_previous_instances():
    try:
        # 現在のプロセス ID を取得
        current_pid = str(os.getpid())
        # sync_text.py を名前に含むプロセスの PID をすべて取得
        pids = subprocess.check_output(["pgrep", "-f", "sync_text_levi.py"]).decode().split()

        # 現在のプロセスを除くすべてのプロセスを終了
        for pid in pids:
            if pid != current_pid:
                os.kill(int(pid), signal.SIGTERM)
    except subprocess.CalledProcessError:
        # pgrep がプロセスを見つけられない場合は何もしない
        pass

def main():
    # Sync the specified directory
    subprocess.run(['rclone', 'sync', f'googledrive:/LEVI/RASPI/{str(pi_idx).zfill(2)}/', f'/home/pi/sync/'])

    # Get the newest text file in the directory
    newest_file = get_random_file(f'/home/pi/sync/')

    if newest_file:
        root = tk.Tk()
        root.title('New Text File Content')
        root.attributes('-fullscreen', True)
        root.configure(bg='black')
        font_settings = ('Meiryo', 20)

        # Create a scrolled text area widget with specified font settings
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg='black', fg='white', font=font_settings)
        text_area.pack(fill=tk.BOTH, expand=True)

        # Read the content of the file and insert it into the text area
        with open(newest_file, 'r') as file:
            content = file.read()
            text_area.insert(tk.INSERT, content)

        def on_close():
            root.destroy()
            sys.exit(0)

        root.protocol("WM_DELETE_WINDOW", on_close)

        root.mainloop()

    # Exit the script
    kill_previous_instances()
    sys.exit(0)

if __name__ == "__main__":
    main()
