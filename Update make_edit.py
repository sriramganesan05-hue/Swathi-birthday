import os
import glob
import numpy as np
import PIL.Image
from PIL import ImageFilter, ImageDraw, ImageFont

# Monkey-patch in case Pillow 10+ is loaded
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'LANCZOS', None) or PIL.Image.Resampling.LANCZOS

from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips
)

WIDTH, HEIGHT = 1080, 1920
FPS = 30
OUTPUT_FILE = "birthday_edit.mp4"
BEAT_FAST = 1.0
BEAT_SLOW = 2.0

def find_audio():
    extensions = ("*.mp3", "*.m4a", "*.wav", "*.aac", "*.ogg", "*.mp4", "*.webm")
    files = []
    for ext in extensions:
        files.extend(glob.glob(ext))
        files.extend(glob.glob(ext.upper()))
    valid_audio = [f for f in files if f != OUTPUT_FILE and not f.endswith('.py')]
    if valid_audio:
        print(f"🎵 Using audio: {valid_audio[0]}")
        return valid_audio[0]
    raise FileNotFoundError("Audio file not found!")

def find_images():
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
    imgs = []
    for ext in extensions:
        imgs.extend(glob.glob(ext))
        imgs.extend(glob.glob(f"images/{ext}"))
    return sorted(list(set(imgs)))

def prepare_frame(img_path, add_text=False):
    img = PIL.Image.open(img_path).convert("RGB")
    
    # Background blur
    bg = img.copy()
    bg_ratio = max(WIDTH / bg.width, HEIGHT / bg.height)
    bg = bg.resize((int(bg.width * bg_ratio), int(bg.height * bg_ratio)))
    left = (bg.width - WIDTH) // 2
    top = (bg.height - HEIGHT) // 2
    bg = bg.crop((left, top, left + WIDTH, top + HEIGHT))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    
    # Center photo
    fg = img.copy()
    fg_ratio = min((WIDTH - 120) / fg.width, (HEIGHT - 320) / fg.height)
    fg = fg.resize((int(fg.width * fg_ratio), int(fg.height * fg_ratio)))
    offset = ((WIDTH - fg.width) // 2, (HEIGHT - fg.height) // 2)
    bg.paste(fg, offset)
    
    if add_text:
        draw = ImageDraw.Draw(bg)
        font = ImageFont.load_default()
        draw.rectangle([(0, HEIGHT - 260), (WIDTH, HEIGHT - 140)], fill=(0, 0, 0, 140))
        draw.text((WIDTH // 2 - 140, HEIGHT - 220), "Happy Birthday Swathi!", fill="white", font=font)
        draw.text((WIDTH // 2 - 130, HEIGHT - 180), "No place I'd rather be", fill="#FFD700", font=font)
        
    return np.array(bg)

def main():
    imgs = find_images()
    if not imgs:
        raise ValueError("No images found in the repository!")
    
    audio_path = find_audio()
    print(f"📸 Found {len(imgs)} photos.")

    clips = []
    for i, path in enumerate(imgs):
        frame = prepare_frame(path, add_text=(i < 2))
        duration = BEAT_FAST if (i % 3 == 0) else BEAT_SLOW
        # Use ImageClip directly (avoids the broken MoviePy resize function)
        c = ImageClip(frame).set_duration(duration)
        clips.append(c)

    video = concatenate_videoclips(clips, method="compose")
    total_len = video.duration

    audio = AudioFileClip(audio_path)
    start_t = 64.0 if audio.duration > (64.0 + total_len) else 0.0
    end_t = min(start_t + total_len, audio.duration)
    
    audio_cut = audio.subclip(start_t, end_t)
    if audio_cut.duration < total_len:
        video = video.subclip(0, audio_cut.duration)
        
    video = video.set_audio(audio_cut)
    video.write_videofile(OUTPUT_FILE, fps=FPS, codec="libx264", audio_codec="aac")
    print("✨ Render completed successfully!")

if __name__ == "__main__":
    main()
