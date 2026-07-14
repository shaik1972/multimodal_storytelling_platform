from gtts import gTTS
import os

def generate_sample_audio():
    text = "Once upon a time, in a magical library, a curious child discovered a glowing doorway that led to endless adventures."
    tts = gTTS(text=text, lang="en")
    
    # Save directly into Next.js public folder
    public_path = os.path.join(os.path.dirname(__file__), "../../ui/public/sample.mp3")
    tts.save(public_path)
    print(f"Sample audio saved to {public_path}")

if __name__ == "__main__":
    generate_sample_audio()

