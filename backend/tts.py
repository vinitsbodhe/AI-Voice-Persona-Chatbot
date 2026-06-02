import uuid
from pathlib import Path
from gtts import gTTS
from backend import config

class TTSManager:
    def __init__(self):
        """
        Initializes the gTTS manager.
        gTTS does not require an API key or client setup.
        """
        pass

    def generate_speech(self, text: str) -> str:
        """
        Generates speech audio using Google's free gTTS engine.
        Saves it to the temporary audio directory and returns the filename.
        """
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        output_path = Path(config.AUDIO_OUTPUT_DIR) / filename

        try:
            # Clean up text to avoid voice glitches
            clean_text = text.replace("*", "").replace("#", "").strip()
            
            # Create gTTS speech object
            tts = gTTS(
                text=clean_text,
                lang=config.TTS_LANG,
                tld=config.TTS_TLD,
                slow=False
            )
            
            # Save to disk
            tts.save(str(output_path))
            print(f"Generated free gTTS audio saved to {output_path}")
            return filename
        except Exception as e:
            print(f"Error during gTTS generation: {e}")
            raise e
            
    def cleanup_old_audio(self):
        """
        Helper method to clean up files in the audio directory to prevent disk bloat.
        """
        import time
        audio_dir = Path(config.AUDIO_OUTPUT_DIR)
        now = time.time()
        # Remove files older than 1 hour (3600 seconds)
        for item in audio_dir.glob("*.mp3"):
            if item.is_file() and (now - item.stat().st_mtime > 3600):
                try:
                    item.unlink()
                    print(f"Cleaned up old audio file: {item.name}")
                except Exception as e:
                    print(f"Error deleting file {item.name}: {e}")
