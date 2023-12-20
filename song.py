import pygame
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv

# Inisialisasi pygame
pygame.mixer.init()

# Nama file lagu (gantilah dengan nama file lagu yang sesuai)
lagu_file = 'alarm2.mp3'

# Fungsi untuk memainkan lagu
def mainkan_lagu():
    pygame.mixer.music.load(lagu_file)
    pygame.mixer.music.play()
    time.sleep(8)  # Menunggu selama 5 detik
    pygame.mixer.music.stop()

# Fungsi yang akan dipanggil saat ada perubahan pada file baca.csv
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('file_plc.csv'):
            with open('file_plc.csv', mode='r') as file:
                reader = csv.reader(file)

                for row in reader:
                    # Mengambil elemen terakhir dari setiap baris
                    last_element = row[-1]
                    
                    # Jika elemen terakhir adalah "NG", lakukan sesuatu
                    if last_element == 'NG':
                        mainkan_lagu()
                        print("SALAH")

# Memulai pemantauan file
observer = Observer()
event_handler = MyHandler()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()

try:
    while True:
        # Biarkan program berjalan terus untuk memantau file
        pass
except KeyboardInterrupt:
    # Hentikan pemantauan saat pengguna menekan Ctrl+C
    observer.stop()

observer.join()
