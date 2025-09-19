## sfx.py
## last updated: 19/09/2025 <d/m/y>
## p-y-l-i
import sys
import os
import warnings
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
stderr = sys.stderr
sys.stderr = open(os.devnull, "w")
import pygame
sys.stderr = stderr
from colorama import *

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
            print(Fore.RED + f"[DEV PRINT] Failed to initialize pygame mixer.\n\ne:{e}")
            print("[DEV PRINT] Sound effects will be disabled." + Style.RESET_ALL)

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
            print(Fore.RED + f"[DEV PRINT] Failed to load sound '{sound_name}'.\n\ne: {e}" + Style.RESET_ALL)
            return False
            
    def play_sound(self, sound_name):
        if not self.mixer_initialized:
            return
        if sound_name not in self.sounds:
            if not self.load_sound(sound_name):
                print(Fore.RED + f"[DEV PRINT] Failed to load and play sound: {sound_name}." + Style.RESET_ALL)
                return        
        try:
            self.sounds[sound_name].play()
        except pygame.error as e:
            print(Fore.RED + f"[DEV PRINT] Failed to play sound '{sound_name}'.\n\ne: {e}")

    def list_available_sounds(self):
        if not self.sound_dir or not os.path.exists(self.sound_dir):
            print(Fore.RED + "[DEV PRINT] Sound directory not found." + Style.RESET_ALL)
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