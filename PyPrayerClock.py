"""
@file       PyPrayerClock.py
@author     Khalid Mansoor AlAwadhi <khalid@remal.io>
@date       Inital Release - Aug 9 2024
@brief      This script creates a GUI to display the current time and upcoming
            prayer times for Dubai, UAE. It fetches prayer times from the Aladhan API
            and plays a random Athan from a specified folder when the prayer time is reached.
            Additionally, clicking on the screen during debugging will trigger the Athan playback.

            Dependencies:
            - tkinter: For creating the GUI.
            - requests: For making API requests to fetch prayer times.
            - pygame: For playing audio files.
            - random: For selecting a random audio file.

            Usage:
            - Make sure to have an "AthanList" folder in the same directory containing Athan audio files.
            - Run the script, and the GUI will display the current time and upcoming prayer times.
            - The Athan will play at the designated prayer times.
"""
import tkinter as tk
from tkinter import Label
import requests
from datetime import datetime, timedelta
import os
import random
import pygame
import time

# Global variable to track if Athan is playing
is_athan_playing = False



def get_prayer_times():
    """
    @brief Fetches the prayer times for Dubai, UAE from the Aladhan API.

    @param None
    
    @return A dictionary containing the prayer times for Fajr, Dhuhr, Asr, Maghrib, and Isha.
    """
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
    """
    @brief Plays a random Athan audio file from the "AthanList" folder.

    @param None
    
    @return None
    """
    global is_athan_playing

    # Get the absolute path of the directory where the script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to the "AthanList" folder inside the script directory
    athan_folder = os.path.join(script_dir, "AthanList")

    if os.path.exists(athan_folder) and os.path.isdir(athan_folder):
        athan_files = [f for f in os.listdir(athan_folder) if os.path.isfile(os.path.join(athan_folder, f))]
        if athan_files:
            selected_athan = random.choice(athan_files)
            print(f"Playing Athan: {selected_athan}")
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(athan_folder, selected_athan))
            
            # Start playing the audio
            pygame.mixer.music.play()
            is_athan_playing = True  # Set flag to indicate Athan is playing

        else:
            print("No Athan files found in the folder.")
    else:
        print("Athan folder does not exist.")



def update_time():
    """
    @brief Updates the current time display and checks if it's time to play the Athan.
           Also determines and updates the next prayer time.
    
    @param None
    
    @return None
    """
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
    root.after(1000, update_time)



def daily_update():
    """
    @brief Fetches the latest prayer times from the API once daily and updates the prayer times in the script.
    
    @param None
    
    @return None
    """
    global prayer_times
    prayer_times = get_prayer_times()
    # Schedule next daily update
    root.after(86400000, daily_update)  # 86400000 ms = 24 hours



def stop_athan(event=None):
    """
    @brief Stops the Athan if it's currently playing.
    
    @param event: Optional event parameter for Tkinter binding.
    
    @return None
    """
    global is_athan_playing

    if is_athan_playing:
        pygame.mixer.music.stop()  # Stop the Athan playback
        is_athan_playing = False   # Reset flag
        print("Athan has been stopped due to screen tap.")



# Initialize the Tkinter root window
root = tk.Tk()
root.title("Prayer Times")
root.configure(bg='black')

# Enable fullscreen mode on startup
root.attributes('-fullscreen', True)

# Exit full-screen mode by pressing the 'Escape' key
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

# Time label with a digital-looking font
digital_font = ("DS-Digital", 150)
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

# Bind the mouse click event to stop the Athan if it's playing
root.bind("<Button-1>", stop_athan)

# Start the Tkinter main loop
root.mainloop()