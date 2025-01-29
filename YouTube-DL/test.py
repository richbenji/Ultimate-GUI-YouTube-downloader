from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "https://www.youtube.com/watch?v=Kfr5G6HLiWQ"

yt = YouTube(url, use_po_token=True, on_progress_callback=on_progress)
print(yt.title)

print(yt.streams.filter(only_audio=True))
#video_streams = yt.streams.filter(adaptive=True, only_video=True)
#options = [f"{stream.resolution}" for stream in video_streams if stream.resolution]
#print(options)

# print(yt.streams.filter(type="audio", bitrate="", resolution="", progressive="", ))
# Télécharge la plus haute résolution
#ys = yt.streams.get_highest_resolution()
#ys.download()

# Télécharge seulement l'audio
#audio = yt.streams.get_audio_only()
#audio.download()

# Affiche quelques caractéristiques des streams
#for stream in yt.streams:
#    print(f"Mime type: {stream.mime_type}, Résolution: {stream.resolution}, Bitrate: {stream.bitrate}")
