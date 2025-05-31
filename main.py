import os
import sys
import threading
import tkinter as tk
from PIL import Image, ImageDraw
import pytesseract
import pyperclip
import keyboard
import ctypes
import pystray
import mss

# ----------------------------------------------------
# 1) Configuración básica de Tesseract y tessdata-dir
# ----------------------------------------------------
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def get_virtual_screen_bounds():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    left   = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
    top    = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
    width  = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
    height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
    return left, top, width, height

def run_ocr():
    left, top, width, height = get_virtual_screen_bounds()

    class ScreenOCR(tk.Tk):
        def __init__(self):
            super().__init__()
            self.overrideredirect(True)
            self.attributes('-alpha', 0.3)
            self.attributes('-topmost', True)
            self.geometry(f"{width}x{height}+{left}+{top}")
            self.config(cursor="cross")

            self.start_x = None
            self.start_y = None
            self.rect = None

            self.canvas = tk.Canvas(self, bg='black')
            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.canvas.bind("<ButtonPress-1>",    self.on_button_press)
            self.canvas.bind("<B1-Motion>",        self.on_move)
            self.canvas.bind("<ButtonRelease-1>",  self.on_button_release)

        def on_button_press(self, event):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y,
                self.start_x, self.start_y,
                outline='red', width=2
            )

        def on_move(self, event):
            self.canvas.coords(
                self.rect,
                self.start_x, self.start_y,
                event.x, event.y
            )

        def on_button_release(self, event):
            end_x = event.x
            end_y = event.y
            x1 = min(self.start_x, end_x) + left
            y1 = min(self.start_y, end_y) + top
            x2 = max(self.start_x, end_x) + left
            y2 = max(self.start_y, end_y) + top

            self.withdraw()  # Oculta la ventana antes de capturar

            with mss.mss() as sct:
                monitor = sct.monitors[0]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

            crop_box = (x1 - left, y1 - top, x2 - left, y2 - top)
            region = img.crop(crop_box)

            texto = pytesseract.image_to_string(region, lang='eng').strip()
            pyperclip.copy(texto)

            if texto:
                print("Texto copiado al portapapeles:")
                print(texto)
            else:
                print("No se detectó texto en la región seleccionada.")
            self.quit()

    app = ScreenOCR()
    app.mainloop()

def create_tray_icon():
    # Construimos la ruta absoluta al ícono, usando __file__
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_icono = os.path.join(base_dir, 'resources', 'icono_ocr.ico')

    try:
        icon_image = Image.open(ruta_icono)
    except Exception as e:
        print(f"No se pudo cargar el ícono: {e}. Se usará un ícono simple por defecto.")
        icon_image = Image.new('RGB', (64, 64), color=(0, 0, 128))
        draw = ImageDraw.Draw(icon_image)
        draw.text((10, 20), "OCR", fill="white")

    def on_exit(icon, item):
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(pystray.MenuItem('Salir', on_exit))
    tray_icon = pystray.Icon("ScreenOCR", icon_image, "ScreenOCR", menu)
    tray_icon.run()

def hotkey_listener():
    def on_hotkey():
        threading.Thread(target=run_ocr, daemon=True).start()

    keyboard.add_hotkey('shift+alt+s', on_hotkey)
    print("Presiona SHIFT+ALT+S para seleccionar una región y hacer OCR.")

if __name__ == '__main__':
    dependencias = [
        ('keyboard',    'keyboard'),
        ('pyperclip',   'pyperclip'),
        ('Pillow',      'PIL'),
        ('pytesseract', 'pytesseract'),
        ('pystray',     'pystray'),
        ('mss',         'mss'),
    ]
    for pkg_name, import_name in dependencias:
        try:
            __import__(import_name)
        except ImportError:
            print(f"Falta instalar {pkg_name}: pip install {pkg_name.lower()}")
            exit(1)

    threading.Thread(target=create_tray_icon, daemon=True).start()
    hotkey_listener()
    keyboard.wait()
