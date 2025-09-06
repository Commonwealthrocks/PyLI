## sfx.py
## last updated: 06/09/2025 <d/m/y>
## p-y-l-i
from importzz import *

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.sound_dir = None
        self.mixer_initialized = False        
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.mixer_initialized = True
            self.sound_dir = self.get_sound_dir()
        except pygame.error as e:
            print(f"[DEV PRINT] Failed to initialize pygame mixer: {e}")
            print("[DEV PRINT] Sound effects will be disabled.")

    def get_sound_dir(self):
        if getattr(sys, "frozen", False):
            return os.path.join(sys._MEIPASS, "sfx")
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")

    def load_sound(self, sound_name):
        if not self.mixer_initialized or not self.sound_dir:
            return False            
        sound_path = os.path.join(self.sound_dir, sound_name)        
        if not os.path.exists(sound_path):
            return False          
        try:
            sound = pygame.mixer.Sound(sound_path)
            self.sounds[sound_name] = sound
            return True
        except pygame.error as e:
            print(f"[DEV PRINT] Failed to load sound '{sound_name}': {e}")
            return False
            
    def play_sound(self, sound_name):
        if not self.mixer_initialized:
            return
            
        if sound_name not in self.sounds:
            if not self.load_sound(sound_name):
                print(f"[DEV PRINT] Failed to load and play sound: {sound_name}")
                return        
        try:
            self.sounds[sound_name].play()
        except pygame.error as e:
            print(f"[DEV PRINT] Failed to play sound '{sound_name}': {e}")

    def list_available_sounds(self):
        if not self.sound_dir or not os.path.exists(self.sound_dir):
            print("[DEV PRINT] Sound directory not found")
            return []            
        sound_files = []
        for file in os.listdir(self.sound_dir):
            if file.lower().endswith((".wav", ".ogg", ".mp3")):
                sound_files.append(file)               
        return sound_files

    def unload(self):
        if self.sounds:
            for sound in self.sounds.values():
                try:
                    sound.stop()
                except:
                    pass
            self.sounds.clear()          
        if self.mixer_initialized:
            try:
                pygame.mixer.quit()
            except:
                pass

## end