import pygame
import time

# Inisialisasi pygame
pygame.mixer.init()

# Nama file lagu (gantilah dengan nama file lagu yang sesuai)
lagu_file = 'alarm2.mp3'

# Memainkan lagu
pygame.mixer.music.load(lagu_file)
pygame.mixer.music.play()

# Menunggu selama 5 detik
time.sleep(5)

# Menghentikan pemutaran lagu
pygame.mixer.music.stop()
