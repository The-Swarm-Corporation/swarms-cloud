import os
from pytube import YouTube


def download_youtube_audio(video_url, output_folder):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream:
            output_file = audio_stream.download(output_path=output_folder)
            # Rename the file to have the .mp3 extension
            mp3_file = output_file.split(".")[0] + ".mp3"
            os.rename(output_file, mp3_file)
            print("Audio downloaded successfully:", mp3_file)
        else:
            print("No audio stream available for the given URL.")
    except Exception as e:
        print("Error:", e)


# Example usage
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example YouTube video URL
output_folder = "youtube_downloads"  # Output folder where the MP3 will be saved
download_youtube_audio(video_url, output_folder)
