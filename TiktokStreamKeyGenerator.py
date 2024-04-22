import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

class Stream:
    def __init__(self, title, game_tag_id, gen_replay=False, close_room_when_close_stream=True, age_restricted=False, priority_region="", stream_server=0):
        self.streamInfo = self.createStream(title, game_tag_id, gen_replay, close_room_when_close_stream, age_restricted, priority_region, stream_server)
        self.created = False
        try:
            self.streamUrl = self.streamInfo["data"]["stream_url"]["rtmp_push_url"]
            split_index = self.streamUrl.rfind("/")
            self.baseStreamUrl = self.streamUrl[:split_index]
            self.streamKey = self.streamUrl[split_index + 1:]
            self.streamShareUrl = self.streamInfo["data"]["share_url"]
            self.created = True
        except:
            if self.streamInfo["data"]["prompts"] == "Please login first":
                messagebox.showerror("Error", "Error creating stream. Try the other server.")
            else:
                messagebox.showerror("Error", self.streamInfo["data"]["prompts"])


    def createStream(self, title, game_tag_id, gen_replay=False, close_room_when_close_stream=True, age_restricted=False, priority_region="", stream_server=0):
        if stream_server == 0:
            url = "https://webcast16-normal-c-useast1a.tiktokv.com/webcast/room/create/" # For some reason some regions don't work with this URL
        else:
            url = "https://webcast16-normal-c-useast2a.tiktokv.com/webcast/room/create/"
        params = {
            "aid": "8311", # App ID for TikTok Live Studio
            "app_name": "tiktok_live_studio", # App name for TikTok Live Studio
            "channel": "studio", # Channel for TikTok Live Studio
            "device_platform": "windows",
            "priority_region": priority_region, # Priority region for the stream
            "live_mode": "6"
        }
        data = {
            "title": title, # Title of stream
            "live_studio": "1",
            "gen_replay": gen_replay, # To generate replay
            "close_room_when_close_stream": close_room_when_close_stream, # To close room when stream is closed
            "hashtag_id": "5", # Gaming hashtag ID
            "game_tag_id": game_tag_id # Game ID find more at https://webcast16-normal-c-useast2a.tiktokv.com/webcast/room/hashtag/list/
        }
        if age_restricted:
            data["age_restricted"] = "4"
        headers = {
            "user-agent": ""
        }
        with open('cookies.json', 'r') as file:
            cookies_file = json.load(file)
        cookies = {}
        for cookie in cookies_file:
            cookies[cookie['name']] = cookie['value']

        with requests.session() as s:
            info = s.post(url, params=params, data=data, headers=headers, cookies=cookies).json()
        return info

def save_config():
    """Save entry values to a JSON file."""
    if game_combobox.get() != '':
        game_id = [game for game in games if games[game] == game_combobox.get()][0]
    else:
        game_id = ''
    data = {
        'title': title_entry.get(),
        'game_tag_id': game_id,
        'priority_region': region_entry.get(),
        'generate_replay': replay_var.get(),
        'selected_server': server_var.get(), 
        'close_room_when_close_stream': close_room_var.get(),
        'age_restricted': age_restricted_var.get()
    }
    with open('config.json', 'w') as file:
        json.dump(data, file)

def load_config():
    """Load entry values from a JSON file."""
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)
        title_entry.delete(0, tk.END)
        title_entry.insert(0, data.get('title', ''))
        game_combobox.set(games.get(data['game_tag_id'], ''))
        region_entry.set(data.get('priority_region', ''))
        server_var.set(data.get('selected_server', 0))
        replay_var.set(data.get('generate_replay', False))
        close_room_var.set(data.get('close_room_when_close_stream', True))
        age_restricted_var.set(data.get('age_restricted', False))
    except:
        print("Error loading config file.")

def check_cookies():
    """Update the label based on the existence of cookies.json."""
    if os.path.exists('cookies.json'):
        cookies_status.config(text="Cookies are loaded")
        go_live_button.config(state=tk.NORMAL)
        login_button.config(state=tk.DISABLED)
    else:
        cookies_status.config(text="No cookies found")
        go_live_button.config(state=tk.DISABLED)
        login_button.config(state=tk.NORMAL)

def wait_for_page_load(driver, timeout=30):
    """Wait for the page's load state to be 'complete'."""
    return WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def launch_browser():
    """Launch Selenium to perform login and save cookies."""
    driver = uc.Chrome()
    driver.get('https://www.tiktok.com/login/phone-or-email')
    try:
        WebDriverWait(driver, 60).until(
            EC.url_contains("https://www.tiktok.com/foryou"))
        cookies = driver.get_cookies()
        with open('cookies.json', 'w') as file:
            json.dump(cookies, file)
        wait_for_page_load(driver)
        driver.quit()
        messagebox.showinfo("Login Status", "Login Successful and cookies saved!")
    except:
        messagebox.showinfo("Login Status", "Login Failed or Timed Out")
    finally:
        driver.quit()
        check_cookies()

def generate_stream():
    """Function for stream key generation."""
    server_entry.config(state=tk.NORMAL)
    key_entry.config(state=tk.NORMAL)
    url_entry.config(state=tk.NORMAL)
    
    if game_combobox.get() != '':
        game_id = [game for game in games if games[game] == game_combobox.get()][0]
    else:
        messagebox.showerror("Error", "Please select a game tag.")
        return
    s = Stream(title_entry.get(), game_id, replay_var.get(), close_room_var.get(), age_restricted_var.get(), region_entry.get(), server_var.get())
    if s.created:
        server_entry.delete(0, tk.END)
        server_entry.insert(0, s.baseStreamUrl)
        key_entry.delete(0, tk.END)
        key_entry.insert(0, s.streamKey)
        url_entry.delete(0, tk.END)
        url_entry.insert(0, s.streamShareUrl)
    else:
        server_entry.delete(0, tk.END)
        key_entry.delete(0, tk.END)
        url_entry.delete(0, tk.END)

    server_entry.config(state=tk.DISABLED)
    key_entry.config(state=tk.DISABLED)
    url_entry.config(state=tk.DISABLED)

def login_thread():
    """Handle the login process in a separate thread to keep UI responsive."""
    threading.Thread(target=launch_browser).start()

def fetch_game_tags():
    url = "https://webcast16-normal-c-useast2a.tiktokv.com/webcast/room/hashtag/list/"
    try:
        response = requests.get(url)
        game_tags = response.json()['data']['game_tag_list']
        return {game['id']: game['show_name'] for game in game_tags}
    except Exception as e:
        print(f"Failed to fetch game tags: {e}")
        return {}

def update_combobox_options(event):
    # Get current text in the combobox
    current_text = game_combobox.get()
    # Filter the games dictionary
    filtered_options = [name for name in games.values() if name.lower().startswith(current_text.lower())]
    # Update the options displayed in the combobox
    game_combobox['values'] = filtered_options


app = tk.Tk()
app.title("TikTok Stream Key Generator")
app.columnconfigure(0, weight=1)  # This makes the first column in the main window expandable
app.rowconfigure(0, weight=1)     # This makes the first row in the main window expandable
app.columnconfigure(1, weight=1)  # This makes the second column in the main window expandable
app.rowconfigure(1, weight=1)     # This makes the second row in the main window expandable

# Using LabelFrames for better organization
input_frame = ttk.LabelFrame(app, text="Input")
input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
input_frame.columnconfigure(1, weight=1)

# Input fields and labels inside the LabelFrame
title_label = ttk.Label(input_frame, text="Title")
title_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

title_entry = ttk.Entry(input_frame)
title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")


game_combobox = ttk.Combobox(input_frame)

game_label = ttk.Label(input_frame, text="Game")
game_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

games = fetch_game_tags()
game_combobox = ttk.Combobox(input_frame, values=list(games.values()))
game_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
game_combobox.bind('<KeyRelease>', update_combobox_options)

region_label = ttk.Label(input_frame, text="Region")
region_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

region_entry = ttk.Combobox(input_frame, values=["", "ar", "bg", "bn-IN", "ceb-PH", "cs-CZ", "da", "de-DE", "el-GR", "en", "es", "et", "fi-FI", "fil-PH", "fr", "he-IL", "hi-IN", "hr", "hu-HU", "id-ID", "it-IT", "ja-JP", "jv-ID", "km-KH", "ko-KR", "lt", "lv", "ms-MY", "my-MM", "nb", "nl-NL", "pl-PL", "pt-BR", "ro-RO", "ru-RU", "sk", "sv-SE", "th-TH", "tr-TR", "uk-UA", "ur", "uz", "vi-VN", "zh-Hant-TW", "zh-Hans"])
region_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

server_var = tk.IntVar(value=0)

radio_server1 = ttk.Radiobutton(input_frame, text="Server 1", variable=server_var, value=0)
radio_server1.grid(row=3, column=0, padx=5, pady=2, sticky="w")

radio_server2 = ttk.Radiobutton(input_frame, text="Server 2", variable=server_var, value=1)
radio_server2.grid(row=3, column=1, padx=5, pady=2, sticky="w")

replay_var = tk.BooleanVar()
replay_checkbox = ttk.Checkbutton(input_frame, text="Generate Replay", variable=replay_var)
replay_checkbox.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="w")

close_room_var = tk.BooleanVar(value=True)
close_room_checkbox = ttk.Checkbutton(input_frame, text="Close Room When Close Stream", variable=close_room_var)
close_room_checkbox.grid(row=5, column=0, columnspan=2, padx=5, pady=2, sticky="w")

age_restricted_var = tk.BooleanVar()
age_restricted_checkbox = ttk.Checkbutton(input_frame, text="Age Restricted", variable=age_restricted_var)
age_restricted_checkbox.grid(row=6, column=0, columnspan=2, padx=5, pady=2, sticky="w")

# Cookies status
cookies_status = ttk.Label(app, text="Checking cookies...")
cookies_status.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

# Buttons
login_button = ttk.Button(app, text="Login", command=login_thread, state=tk.DISABLED)
login_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

go_live_button = ttk.Button(app, text="Go Live", command=generate_stream, state=tk.DISABLED)
go_live_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

save_config_button = ttk.Button(app, text="Save Config", command=save_config)
save_config_button.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

# Outputs
output_frame = ttk.LabelFrame(app, text="Outputs")
output_frame.grid(row=0, column=1, rowspan=5, padx=10, pady=5, sticky="nsew")
output_frame.columnconfigure(0, weight=1)

server_entry = ttk.Entry(output_frame, state="readonly")
server_entry.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

key_entry = ttk.Entry(output_frame, state="readonly")
key_entry.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

url_entry = ttk.Entry(output_frame, state="readonly")
url_entry.grid(row=2, column=0, padx=5, pady=2, sticky="ew")

def copy_to_clipboard(content):
    app.clipboard_clear()
    app.clipboard_append(content)
    messagebox.showinfo("Copied", "Content copied to clipboard!")

# Copy buttons for each Entry
copy_server_button = ttk.Button(output_frame, text="Copy", command=lambda: copy_to_clipboard(server_entry.get()))
copy_server_button.grid(row=0, column=1, padx=5, pady=2)

copy_key_button = ttk.Button(output_frame, text="Copy", command=lambda: copy_to_clipboard(key_entry.get()))
copy_key_button.grid(row=1, column=1, padx=5, pady=2)

copy_url_button = ttk.Button(output_frame, text="Copy", command=lambda: copy_to_clipboard(url_entry.get()))
copy_url_button.grid(row=2, column=1, padx=5, pady=2)

check_cookies()
load_config()

app.mainloop()
