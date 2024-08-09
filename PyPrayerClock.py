import tkinter as tk
from tkinter import Label
import requests
from datetime import datetime, timedelta
import os
import random
import pygame

def get_prayer_times():
    url = "http://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": "Dubai",
        "country": "UAE",
        "method": 16  # Specific method for Dubai
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        timings = data['data']['timings']
        # Only consider Fajr, Dhuhr, Asr, Maghrib, and Isha
        prayer_times = {prayer: timings[prayer] for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]}
        return prayer_times
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

def play_athan():
    athan_folder = "AthanList"
    if os.path.exists(athan_folder) and os.path.isdir(athan_folder):
        athan_files = [f for f in os.listdir(athan_folder) if os.path.isfile(os.path.join(athan_folder, f))]
        if athan_files:
            selected_athan = random.choice(athan_files)
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(athan_folder, selected_athan))
            pygame.mixer.music.play()
        else:
            print("No Athan files found in the folder.")
    else:
        print("Athan folder does not exist.")

def update_time():
    # Update current time without seconds
    current_time = datetime.now().strftime("%I:%M %p")
    time_label.config(text=current_time)
    
    # Determine the next prayer time
    now = datetime.now()
    next_prayer = None
    for prayer, time_str in prayer_times.items():
        prayer_time = datetime.strptime(time_str, "%H:%M")
        prayer_time = now.replace(hour=prayer_time.hour, minute=prayer_time.minute, second=0, microsecond=0)
        if now < prayer_time:
            next_prayer = (prayer, prayer_time.strftime("%I:%M %p"))
            break
    
    # If all today's prayers have passed, show Fajr of the next day
    if next_prayer is None:
        tomorrow = now + timedelta(days=1)
        prayer_time = datetime.strptime(prayer_times["Fajr"], "%H:%M")
        prayer_time = tomorrow.replace(hour=prayer_time.hour, minute=prayer_time.minute, second=0, microsecond=0)
        next_prayer = ("Fajr", prayer_time.strftime("%I:%M %p"))
    
    # Check if it's time for the current prayer and play Athan
    current_prayer_time = datetime.now().replace(second=0, microsecond=0).strftime("%I:%M %p")
    if current_prayer_time in prayer_times.values():
        play_athan()

    next_prayer_label.config(text=f"Next Prayer: {next_prayer[0]} at {next_prayer[1]}")
    
    # Schedule to update the time every minute
    root.after(60000, update_time)

def daily_update():
    global prayer_times
    prayer_times = get_prayer_times()
    # Schedule next daily update
    root.after(86400000, daily_update)  # 86400000 ms = 24 hours

# Initialize the Tkinter root window
root = tk.Tk()
root.title("Prayer Times")
root.configure(bg='black')
root.geometry("800x600")  # Set the size of the window

# Time label with a digital-looking font
digital_font = ("DS-Digital", 72)  # You can replace with a similar digital font available on your system
time_label = Label(root, font=digital_font, fg="white", bg="black")
time_label.pack(expand=True)

# Next prayer label
next_prayer_label = Label(root, font=("Helvetica", 24), fg="white", bg="black")
next_prayer_label.pack(side="bottom", pady=20)

# Center the clock and next prayer information
time_label.place(relx=0.5, rely=0.4, anchor='center')
next_prayer_label.place(relx=0.5, rely=0.9, anchor='center')

# Start the daily update and time update loop
daily_update()
update_time()

# Start the Tkinter main loop
root.mainloop()
