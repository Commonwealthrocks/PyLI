## importzz.py
## last updated: 01/9/2025 <d/m/y>
## p-y-l-i

import warnings
import sys
import os
import json
import hashlib
import struct
import secrets
import base64
import ctypes
import argparse
import getpass
import reedsolo
import zlib
import lzma
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")
import pygame
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCore import Signal as pyqtSignal
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

## end