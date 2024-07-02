import os, io, urllib.request, time
import tkinter as tk
import customtkinter as ctk
from pygame import mixer
from youtube_search import YoutubeSearch
from pytube import YouTube
from moviepy.editor import *
from PIL import ImageTk, Image
from mutagen.mp3 import MP3

class App():
    """
    Class written to store utility functions of the app.
    @Constructor : None
    """
        
    def clear_dir(dir_path):
        """
        Given a directory path, deletes all items inside that directory.
        @Params : [dir_path : str]
        @returns : None
        """
        try:
            mixer.music.stop()
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    os.unlink(entry.path)
            print("All files deleted successfully.")
        except OSError:
            print("Error occurred while deleting files.")

    def setup_track(search_query):
        """
        Given a search query, forms an mp3 file with the first youtube video that comes up with the search query.
        @Params : [search_query : str]
        @returns : None
        """
        global app_image, audio_length, song_title_label, start_time, paused, song_end_notify, current_offset
        try:
            search_results = YoutubeSearch(search_query, max_results=1).to_dict()
            image = App.fetch_img(search_results[0]["thumbnails"][0])
            app_image.configure(image=image)
            base_link = "https://www.youtube.com/" + search_results[0]["url_suffix"]
            SAVE_PATH = './hysk13_musicplayer_downloads'
            App.clear_dir('./hysk13_musicplayer_downloads')
            youtube = YouTube(base_link)
            mp4_streams = youtube.streams.filter(file_extension='mp4').all()
            d_video = mp4_streams[-1]
            d_video.download(output_path=SAVE_PATH)
            video = AudioFileClip("./hysk13_musicplayer_downloads/" + os.listdir('./hysk13_musicplayer_downloads')[0])
            video.write_audiofile("./hysk13_musicplayer_downloads/example.mp3")
            audio_length = MP3("./hysk13_musicplayer_downloads/example.mp3").info.length
            song_title_label.configure(text=search_results[0]["title"])
            mixer.music.load(f'./hysk13_musicplayer_downloads/example.mp3')
            mixer.music.play()
            start_time = time.time()
            paused = False
            song_end_notify = False
            current_offset = 0
        except Exception:
            print("Error has occured while downloading the track.")

    def fetch_img(base_url):
        """
        Given a directory path, deletes all items inside that directory.
        @Params : [base_url : str]
        @returns : ImageTk.PhotoImage
        """
        with urllib.request.urlopen(base_url) as u:
            raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        return ImageTk.PhotoImage(image)
    
    def on_song_end():
        """
        A handler function for when the track comes to an end.
        @Params: None
        @returns: None
        """
        global song_end_notify, repeat_track
        song_end_notify = True
        if repeat_track:
            global start_time, paused, current_offset
            start_time = time.time()
            paused = False
            song_end_notify = False
            current_offset = 0
            mixer.music.play()
        else:
            mixer.music.stop()
            mixer.music.unload()
    

class Commands():
    """
    Class written to store button commands of the app.
    @Constructor : None
    """

    def search_track():
        """
        A handler function for when clicking the "Search" button.
        @Params: None
        @returns: None
        """

        def fetch_search_query():
            """
            A nested function for processing the search_query variable.
            @Params: None
            @returns: None
            """
            global search_query, search_btn
            search_query = search_box.get("1.0", "end")
            App.setup_track(search_query)
            search_frame.destroy()
            search_btn.pack()

        def close_search():
            """
            A nested function for closing the search frame.
            @Params: None
            @returns: None
            """
            search_frame.destroy()
            search_btn.pack()

        global search_btn

        search_btn.pack_forget()

        search_frame = ctk.CTkFrame(window, width=300, height=300)
        search_frame.place(x=200, y=200, anchor=tk.CENTER)

        search_box = ctk.CTkTextbox(search_frame, width=300, height=250, font=BUTTON_FONT)
        search_box.pack(side=tk.TOP, padx=5, pady=5)

        search_btns_frame = ctk.CTkFrame(search_frame, width=300, height=100)
        search_btns_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        enter_btn = ctk.CTkButton(search_btns_frame, text="Search", command=fetch_search_query)
        enter_btn.pack(side=tk.LEFT, padx=5, pady=5)

        close_btn = ctk.CTkButton(search_btns_frame, text="Close", command=close_search)
        close_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def rewind_handle():
        """
        Rewinds the track 5 seconds behind. If it goes before the 0 millisecond mark, than rewinds to the beginning.
        @Params: None
        @returns: None
        """
        global current, current_offset
        if current - 5 < 0:
            mixer.music.set_pos(current - 5)
            current_offset -= 5
        else:
            mixer.music.set_pos(0)
            current_offset += 0 - current

    def play_handle():
        """
        Resumes the track if paused, pauses the track if playing.
        @Params: None
        @returns: None
        """
        global paused
        if mixer.music.get_busy():
            paused = True
            mixer.music.pause()
        else:
            paused = False
            mixer.music.unpause()

    def loop_handle():
        """
        Turns on/off the "repeat track" feature of the GUI.
        @Params: None
        @returns: None
        """
        global repeat_track, loop_btn
        if repeat_track:
            loop_btn.configure(text_color="white")
            repeat_track = False
        else:
            loop_btn.configure(text_color="gray")
            repeat_track = True

    def fastforward_handle():
        """
        Fast forwards the track 5 seconds forward. If it goes beyond the end of the track, then fast forwards to the end.
        @Params: None
        @returns: None
        """
        global audio_length, current, current_offset
        if current + 5 < audio_length:
            mixer.music.set_pos(current + 5)
            current_offset += 5
        else:
            mixer.music.set_pos(audio_length)
            current_offset += audio_length - current
            
current_track = None
start_time = None
audio_length = None

track_pause = True
paused = True
repeat_track = False
song_end_notify = False

search_query = ""
current_theme = "dark"

current_offset = 0

BUTTON_FONT = ("Helvetica", 20, "bold")

if not os.path.exists('./hysk13_musicplayer_downloads'):
    os.mkdir('hysk13_musicplayer_downloads')

mixer.init()
App.clear_dir('./hysk13_musicplayer_downloads')

window = ctk.CTk()
window.title("Music Player")
window.geometry("400x400")
window.resizable(False, False)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

image = App.fetch_img("https://raw.githubusercontent.com/hysk13/musicweb/main/blank2.png")         
app_image = ctk.CTkLabel(window, text="", image=image, width=250, height=250)
app_image.place(x=200, y=150, anchor=tk.CENTER)

song_title_label = ctk.CTkLabel(window, text="Nothing is Playing", font=BUTTON_FONT)
song_title_label.place(x=200, y=250, anchor=tk.CENTER)

buttons_cont = ctk.CTkFrame(window, width=250, height=100, fg_color="transparent")
buttons_cont.place(x=200, y=325, anchor=tk.CENTER)
rewind_btn = ctk.CTkButton(buttons_cont, text="<<", font=BUTTON_FONT, width=50, height=50, command=Commands.rewind_handle)
rewind_btn.pack(side=tk.LEFT, padx=5)
play_btn = ctk.CTkButton(buttons_cont, text=f"▶", font=BUTTON_FONT, width=50, height=50, command=Commands.play_handle)
play_btn.pack(side=tk.LEFT, padx=5)
loop_btn = ctk.CTkButton(buttons_cont, text="♾️", font=BUTTON_FONT, width=50, height=50, command=Commands.loop_handle)
loop_btn.pack(side=tk.LEFT, padx=5)
fast_forward_btn = ctk.CTkButton(buttons_cont, text=">>", font=BUTTON_FONT, width=50, height=50, command=Commands.fastforward_handle)
fast_forward_btn.pack(side=tk.LEFT, padx=5)
top_menu = ctk.CTkFrame(window, width=100, height=100)
top_menu.place(x=390, y=30, anchor=tk.E)
search_btn = ctk.CTkButton(top_menu, text="Search", font=BUTTON_FONT, width=40, height=40, command=Commands.search_track)
search_btn.pack(side=tk.RIGHT, padx=5)

music_progress = ctk.CTkProgressBar(window)
music_progress.place(x=200, y=275, anchor=tk.CENTER)
music_progress.set(0)

while True:
    if mixer.music.get_busy():
        current = time.time() - start_time + current_offset
        music_progress.set(current / audio_length)
    if not mixer.music.get_busy() and not paused and not song_end_notify:
        App.on_song_end()
    window.update()