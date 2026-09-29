import os
import glob
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips
)

WIDTH, HEIGHT = 1080, 1920
FPS = 30
OUTPUT_FILE = "birthday_edit.mp4"
SONG_START_TIME = 64.0  # Starts at the chorus drop

BEAT_FAST = 0.99
BEAT_SLOW = 1.98

def find_audio():
    # Find any mp3/m4a/wav file in the repo
    audio_files = glob.glob("*.mp3") + glob.glob("*.m4a") + glob.glob("*.wav")
    if audio_files:
        return audio_files[0]
    return "rather_be.mp3"

def find_images():
    # Grab all uploaded jpg and png files
    imgs = sorted(glob.glob("*.jpg") + glob.glob("*.jpeg") + glob.glob("*.png"))
    return imgs

def prepare_frame(img_path, add_text=False):
    img = Image.open(img_path).convert("RGB")
    
    # Background blur
    bg = img.copy()
    bg_ratio = max(WIDTH / bg.width, HEIGHT / bg.height)
    bg = bg.resize((int(bg.width * bg_ratio), int(bg.height * bg_ratio)), Image.Resampling.LANCZOS)
    left = (bg.width - WIDTH) // 2
    top = (bg.height - HEIGHT) // 2
    bg = bg.crop((left, top, left + WIDTH, top + HEIGHT))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    
    # Foreground photo
    fg = img.copy()
    fg_ratio = min((WIDTH - 120) / fg.width, (HEIGHT - 320) / fg.height)
    fg = fg.resize((int(fg.width * fg_ratio), int(fg.height * fg_ratio)), Image.Resampling.LANCZOS)
    offset = ((WIDTH - fg.width) // 2, (HEIGHT - fg.height) // 2)
    bg.paste(fg, offset)
    
    if add_text:
        draw = ImageDraw.Draw(bg)
        try:
            font1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
            font2 = ImageFont.truetype("DejaVuSans.ttf", 38)
        except:
            font1 = font2 = ImageFont.load_default()
            
        draw.text((WIDTH // 2, HEIGHT - 240), "Happy Birthday Swathi ✨", fill="white", anchor="mm", font=font1)
        draw.text((WIDTH // 2, HEIGHT - 170), "No place I'd rather be ❤️", fill="#FFD700", anchor="mm", font=font2)
        
    return np.array(bg)

def create_zoom_clip(frame_np, duration):
    clip = ImageClip(frame_np).set_duration(duration)
    return clip.resize(lambda t: 1.0 + 0.08 * (t / duration))

def main():
    image_paths = find_images()
    audio_path = find_audio()
    
    print(f"Using audio: {audio_path}")
    print(f"Found {len(image_paths)} images.")

    clips = []
    for i, path in enumerate(image_paths):
        frame = prepare_frame(path, add_text=(i < 2))
        duration = BEAT_FAST if (i % 3 == 0) else BEAT_SLOW
        c = create_zoom_clip(frame, duration)
        c = c.crossfadein(0.15)
        clips.append(c)

    video = concatenate_videoclips(clips, method="compose", padding=-0.15)
    total_len = video.duration

    audio = AudioFileClip(audio_path)
    audio = audio.subclip(SONG_START_TIME, SONG_START_TIME + total_len).audio_fadeout(2.0)
    video = video.set_audio(audio)

    video.write_videofile(OUTPUT_FILE, fps=FPS, codec="libx264", audio_codec="aac", threads=4)
    print("Done!")

if __name__ == "__main__":
    main()
