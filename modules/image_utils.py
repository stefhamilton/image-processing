import subprocess

def convert_heic_to_jpg_ffmpeg(heic_file, jpg_file):
    try:
        command = ["ffmpeg", "-y", "-i", heic_file, jpg_file]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {heic_file}: {e}")