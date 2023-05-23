import speech_recognition as sr
import nltk
from moviepy.video.fx.all import crop
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
from tkinter import messagebox
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import Tk
from tkinter import Label
from tkinter import E
from tkinter import W
from tkinter import EW
from tkinter import NSEW
from tkinter import Button
from tkinter import Entry
from tkinter import StringVar
import os
from collections import Counter
from threading import *
import time
from tkVideoPlayer import TkinterVideo
from pytube import YouTube
from pytube import Search
import requests
from tqdm import *

window = Tk()
window.title("Video Editor")
window.geometry("265x420")
window.maxsize(265, 420)
window.minsize(265, 420)
window.config(bg="lightgrey")

title = ''
downloaded = False
color_code = ''

Label(window, text="Title", bg="lightgrey").grid(
    row=0, column=0, padx=5, pady=5, sticky=E)
entry_title = Entry(window, bd=3)
entry_title.grid(row=0, column=1, columnspan=6, padx=5, pady=5, sticky="ew")

Label(window, text="Audio", bg="lightgrey").grid(
    row=1, column=0, padx=5, pady=5, sticky=E)
entry_audio_path = Entry(window, bd=4)
entry_audio_path.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

Label(window, text="Music", bg="lightgrey").grid(
    row=2, column=0, padx=5, pady=5, sticky=E)
music_audio_path = Entry(window, bd=4)
music_audio_path.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

Label(window, text="Color", bg="lightgrey").grid(
    row=3, column=0, padx=5, pady=5, sticky=E)
entry_color = Entry(window, bd=4)
entry_color.grid(row=3, column=1, padx=5, pady=5, sticky="ew")


def run_downloading_thread():
    t1 = Thread(target=download_video_related2audio)
    t1.start()


def run_output_thread():
    t1 = Thread(target=output_video)
    t1.start()


def select_audio():
    files = [('MP3 Files', '*.mp3'),
             ('wmv Files', '*.wmv'),
             ('All Files', '*.*')]
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=files,
                                          defaultextension=files)
    audio_path = filename.strip()
    entry_audio_path.delete(0, "end")
    entry_audio_path.insert(-1, audio_path)

# Function that will be invoked when the
# color button will be clicked in the main window


def select_music():
    files = [('MP3 Files', '*.mp3'),
             ('wmv Files', '*.wav'),
             ('All Files', '*.*')]
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=files,
                                          defaultextension=files)
    music_path = filename.strip()
    music_audio_path.delete(0, "end")
    music_audio_path.insert(-1, music_path)

# Function that will be invoked when the
# color button will be clicked in the main window


def choose_color():
    # variable to store hexadecimal code of color
    color_code = colorchooser.askcolor(title="Choose color")[1]
    entry_color.delete(0, "end")
    entry_color.insert(-1, color_code)


btnGetAudio = Button(window, text="Browse", command=select_audio)
btnGetAudio.grid(row=1, column=2, columnspan=2, sticky=EW, padx=5, pady=5)

btnGetMusic = Button(window, text="Browse", command=select_music)
btnGetMusic.grid(row=2, column=2, columnspan=2, sticky=EW, padx=5, pady=5)

btnGetColor = Button(window, text="Color", command=choose_color)
btnGetColor.grid(row=3, column=2, columnspan=2, sticky=EW, padx=5, pady=5)

Label(window, text="Speech", bg="lightgrey").grid(
    row=4, column=0, padx=5, pady=5, sticky=E)
entry_speech = Entry(window, bd=3)
entry_speech.grid(row=4, column=1, columnspan=6, padx=5, pady=5, sticky=EW)

videoplayer = TkinterVideo(master=window, scaled=True, height=10)
videoplayer.grid(row=5, column=0, rowspan=6, columnspan=6,
                 padx=7, pady=10, sticky=NSEW)

btn_search_text = StringVar()
myOutputButton = Button(window, text="Output", command=run_output_thread)
myRecognitionButton = Button(
    window, textvariable=btn_search_text, command=run_downloading_thread)
btn_search_text.set("Search & Download")
myRecognitionButton.grid(row=12, column=0, columnspan=3,
                         padx=10, pady=10, sticky=E)
myOutputButton.grid(row=12, column=3, columnspan=3, padx=10, pady=10, sticky=W)


def get_most_frequent_words(text):
    split_it = text.split()
    print(' '.join(split_it))
    counter = Counter(split_it)
    most_occur = counter.most_common(3)

    frequent_words = ''
    for i in range(min(3, len(most_occur))):
        word, count = most_occur[i]
        frequent_words += ' ' + word
    print('Most frequent words in audio is ' + frequent_words)
    return frequent_words


def download_sample_video():
    try:
        sample_video_url = "https://download.samplelib.com/mp4/sample-5s.mp4"
        print("downloading sample video : " + sample_video_url)
        r = requests.get(sample_video_url, stream=True)
        with open("org_video.mp4", 'wb') as f:
            r.raise_for_status()
            pbar = tqdm(total=int(r.headers['Content-Length']))
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    except Exception as e:
        print("Could not download file {}".format(sample_video_url))


def recognize_audio(audio_path):
    print('Recognizing audio : ' + audio_path + ' ...')
    speech = ''
    entry_speech.delete(0, "end")
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)  # read the entire audio file
    try:
        speech = r.recognize_google(audio)
        print(speech)
        entry_speech.insert(-1, "Recognition: " + speech)
    except sr.UnknownValueError:
        entry_speech.insert(-1,
                            "Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        entry_speech.insert(
            -1, "Could not request results from Google Speech Recognition service; {0}".format(e))
    return speech


def get_youtube_video_urls(keywords):
    print("Searching youtube video with keyword : " + keywords)
    btn_search_text.set("Searching video...")
    try:
        s = Search(keywords)
        return s.results
    except:
        print("Searching youtube video failed ...")
    return []


def download_youtube_video(url):
    print("Trying to download : {}".format(url))
    try:
        youtube_obj = YouTube(url)
        # mp4files = youtube_obj.streams.filter('mp4')
        # youtube_obj.set_filename('org_video.mp4')
        # d_video = youtube_obj.get(mp4files[-1].extension, mp4files[-1].resolution)
        d_video = youtube_obj.streams.get_highest_resolution()
        try:
            d_video.download(os.path.dirname(
                os.path.realpath(__file__)), "org_video.mp4")
            print('downloading video completed! :' + url)
            return True
        except:
            print('downloading video failed! :' + url)
    except Exception as e:
        print("Could not download file {}".format(url))
        return False


def download_video_related2audio():
    btn_search_text.set("Recognizing audio ...")
    myRecognitionButton["state"] = "disabled"
    audio_path = entry_audio_path.get()
    if (audio_path == ''):
        audio_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "audio_EN.mp3")

    speech = recognize_audio(audio_path)

    is_downloaded = False
    keywords = get_most_frequent_words(speech)
    for v in get_youtube_video_urls(keywords):
        time.sleep(1)
        is_downloaded = download_youtube_video(
            'https://www.youtube.com/watch?v=' + v.video_id)
        if (is_downloaded == True):
            break

    if (is_downloaded == False):
        download_sample_video()

    btn_search_text.set("Search & Download")
    myRecognitionButton["state"] = "normal"


def output_video():
    audio_path = entry_audio_path.get()
    music_path = music_audio_path.get()
    color_code = entry_color.get()
    title = entry_title.get()
    if (audio_path == ''):
        messagebox.showerror("Error", "Please fill the audio field.")
        return
    if (title == ''):
        messagebox.showerror("Error", "Please fill the title field.")
        return
    if (color_code == ''):
        color_code = 'lightgreen'

    org_video_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "org_video.mp4")
    final_video_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "final_video.mp4")

    video_clip = VideoFileClip(org_video_path)
    w, h = video_clip.size
    fps = video_clip.fps

    video_clip = video_clip.resize(((w * (1920 / 1080)), 1920))
    # video_clip = cropClip.resize(width=1080)
    video_clip = moviepy.video.fx.all.crop(
        video_clip, width=1080, height=1920, x_center=w/2, y_center=h)

    if (music_path != ''):
        music_clip = AudioFileClip(music_path)
        # new_music_clip = CompositeAudioClip([video_clip.audio, music_clip])
        music_clip = moviepy.audio.fx.all.audio_loop(
            music_clip, duration=video_clip.duration)
        video_clip.audio = music_clip

    w, h = video_clip.size
    fps = video_clip.fps

    intro_duration = 2
    intro_text = TextClip(title, fontsize=100, color='lightgreen',
                          bg_color=color_code, font="Arial-bold", kerning=5, size=video_clip.size)
    intro_text = intro_text.set_duration(intro_duration)
    intro_text = intro_text.set_fps(fps)
    intro_text = intro_text.set_pos("center")

    text = entry_speech.get()
    if (text == ''):
        text = recognize_audio(audio_path)
    sentences = text.split(".")

    text_show_count = (int)(video_clip.reader.duration / 5)
    if (text_show_count > len(sentences)):
        text_show_count = len(sentences)

    watermark_size = 50
    text_clips = []
    for x in range(text_show_count):
        watermark_text = TextClip(sentences[x], fontsize=watermark_size, color='white',
                                  font="Arial-bold", align='south', method='caption', size=video_clip.size)
        watermark_text = watermark_text.set_fps(fps)
        watermark_text = watermark_text.set_duration(5)
        watermark_text = watermark_text.set_start(5 * x)
        watermark_text = watermark_text.margin(
            left=100, right=100, bottom=20, opacity=0)
        watermark_text = watermark_text.set_position(("bottom"))
        watermark_text = watermark_text.crossfadein((1.0))
        text_clips.append(watermark_text)

    watermarked_clip = CompositeVideoClip(
        [video_clip] + text_clips, size=video_clip.size)
    watermarked_clip = watermarked_clip.set_duration(
        video_clip.reader.duration)
    watermarked_clip = watermarked_clip.set_fps(fps)
    watermarked_clip = watermarked_clip.set_audio(video_clip.audio)

    final_clip = concatenate_videoclips(
        [intro_text, watermarked_clip], padding=-1)
    final_clip.write_videofile(
        final_video_path, codec='libx264', audio_codec="aac")

    watermarked_clip.close()
    video_clip.close()
    final_clip.close()

    videoplayer.load("final_video.mp4")
    videoplayer.play()


window.mainloop()
