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

def kill_previous_instances():
    try:
        current_pid = str(os.getpid())
        pids = subprocess.check_output(["pgrep", "-f", "sync_text_levi.py"]).decode().split()

        for pid in pids:
            if pid != current_pid:
                os.kill(int(pid), signal.SIGTERM)
    except subprocess.CalledProcessError:
        pass

def display_text_animated(text, text_area, idx=0):
    """ テキストを一文字ずつアニメーション表示する関数 """
    if idx < len(text):
        current_char = text[idx]
        text_area.insert(tk.END, current_char)
        # 次の文字の表示までの遅延をランダムに設定
        delay = random.uniform(0.01, 0.3)

        # 文字と文字の間のスペースをランダムに設定
        space_length = random.uniform(0.55, 1.1)
        space = ' ' * int(space_length)
        text_area.insert(tk.END, space)

        idx += 1
        text_area.after(int(delay * 1000), lambda: display_text_animated(text, text_area, idx))

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
        font_settings = ('Meiryo', 24)

        # Create a scrolled text area widget with specified font settings
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg='black', fg='white', font=font_settings)
        text_area.pack(fill=tk.BOTH, expand=True)

        # Read the content of the file and insert it into the text area
        with open(newest_file, 'r') as file:
            content = file.read()
            
        display_text_animated(content, text_area)

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
