import os
import threading
import tkinter as tk
from PIL import ImageGrab, Image, ImageDraw
import pytesseract
import pyperclip
import keyboard
import ctypes
import pystray
import sys

# ----------------------------------------------------
# 1) Configuración básica de Tesseract y tessdata-dir
# ----------------------------------------------------
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def get_virtual_screen_bounds():
    """
    Usa ctypes para obtener las dimensiones del "escritorio virtual" en Windows:
    SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN.
    Devuelve (left, top, width, height).
    """
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()

    left   = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
    top    = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
    width  = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
    height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
    return left, top, width, height

def run_ocr():
    """
    Muestra una ventana semitransparente que abarca TODO el escritorio virtual.
    Permite arrastrar un rectángulo con el ratón, captura esa región y hace OCR.
    """
    left, top, width, height = get_virtual_screen_bounds()

    # DEBUG: imprime las dimensiones de todo el escritorio virtual
    print(f"[DEBUG] Escritorio virtual -> left={left}, top={top}, "
          f"width={width}, height={height}")

    class ScreenOCR(tk.Tk):
        def __init__(self):
            super().__init__()
            # Quita bordes y barra de título; transparencia y siempre encima
            self.overrideredirect(True)
            self.attributes('-alpha', 0.3)
            self.attributes('-topmost', True)
            # Coloca la ventana exactamente en (left, top) con tamaño (width x height)
            self.geometry(f"{width}x{height}+{left}+{top}")
            self.config(cursor="cross")

            self.start_x_rel = None
            self.start_y_rel = None
            self.rect = None

            # Un canvas negro semitransparente para dibujar el rectángulo
            self.canvas = tk.Canvas(self, bg='black')
            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.canvas.bind("<ButtonPress-1>",    self.on_button_press)
            self.canvas.bind("<B1-Motion>",        self.on_move)
            self.canvas.bind("<ButtonRelease-1>",  self.on_button_release)

        def on_button_press(self, event):
            # Coordenadas relativas (dentro del canvas) donde empezó el clic
            self.start_x_rel = event.x
            self.start_y_rel = event.y
            self.rect = self.canvas.create_rectangle(
                self.start_x_rel, self.start_y_rel,
                self.start_x_rel, self.start_y_rel,
                outline='red', width=2
            )

        def on_move(self, event):
            # Mientras arrastras, actualiza el tamaño del rectángulo
            self.canvas.coords(
                self.rect,
                self.start_x_rel, self.start_y_rel,
                event.x, event.y
            )

        def on_button_release(self, event):
            end_x_rel = event.x
            end_y_rel = event.y

            # Calcula las coordenadas absolutas dentro de la pantalla virtual
            x1_abs = min(self.start_x_rel, end_x_rel) + left
            y1_abs = min(self.start_y_rel, end_y_rel) + top
            x2_abs = max(self.start_x_rel, end_x_rel) + left
            y2_abs = max(self.start_y_rel, end_y_rel) + top

            # DEBUG: imprime las coordenadas absolutas seleccionadas
            print(f"[DEBUG] Selector terminó en absolutas -> "
                  f"x1={x1_abs}, y1={y1_abs}, x2={x2_abs}, y2={y2_abs}")

            # Oculta la ventana para no capturarla
            self.withdraw()

            # Captura TODO el escritorio virtual usando bbox
            full_screenshot = ImageGrab.grab(
                bbox=(left, top, left + width, top + height)
            )

            # DEBUG: revisa el tamaño de la imagen completa
            w_full, h_full = full_screenshot.size
            print(f"[DEBUG] Tamaño full_screenshot -> width={w_full}, height={h_full}")

            # Calcula el rect dentro de la imagen completa (coordenadas relativas)
            crop_box = (
                x1_abs - left,
                y1_abs - top,
                x2_abs - left,
                y2_abs - top
            )

            # DEBUG: muestra el crop_box que usaremos
            print(f"[DEBUG] crop_box relativo en full_screenshot -> {crop_box}")

            # Recorta esa región y la procesa con OCR
            region = full_screenshot.crop(crop_box)
            texto = pytesseract.image_to_string(region, lang='eng').strip()

            # DEBUG: si la región está en blanco, imprime un mensaje
            if not texto:
                print("[DEBUG] El OCR devolvió cadena vacía. Tal vez la región está fuera de bounds o sin texto.")

            pyperclip.copy(texto)
            print("Texto copiado al portapapeles:")
            print(texto)
            self.quit()

    app = ScreenOCR()
    app.mainloop()

def create_tray_icon():
    """
    Crea un icono en la bandeja con un menú para salir.
    """
    icon_image = Image.new('RGB', (64, 64), color=(0, 0, 128))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 0, 128))
    draw.text((10, 20), "OCR", fill="white")

    def on_exit(icon, item):
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(pystray.MenuItem('Exit', on_exit))
    tray_icon = pystray.Icon("ScreenOCR", icon_image, "ScreenOCR", menu)
    tray_icon.run()

def hotkey_listener():
    """
    Registra la hotkey global SHIFT+ALT+S.
    Cuando la detecta, arranca run_ocr() en un hilo aparte.
    """
    def on_hotkey():
        print("🔔 Hotkey SHIFT+ALT+S detectada. Abriendo selección de pantalla…")
        threading.Thread(target=run_ocr, daemon=True).start()

    keyboard.add_hotkey('shift+alt+s', on_hotkey)
    print("🔔 Listener activo: presiona SHIFT+ALT+S en ANY DE TUS PANTALLAS…")
    keyboard.wait()

if __name__ == '__main__':
    # Verifica dependencias antes de arrancar
    dependencias = [
        ('keyboard',    'keyboard'),
        ('pyperclip',   'pyperclip'),
        ('Pillow',      'PIL'),
        ('pytesseract', 'pytesseract'),
        ('pystray',     'pystray'),
    ]
    for pkg_name, import_name in dependencias:
        try:
            __import__(import_name)
        except ImportError:
            print(f"Falta instalar {pkg_name}: pip install {pkg_name.lower()}")
            exit(1)

    # Lanza icono en bandeja en segundo plano
    threading.Thread(target=create_tray_icon, daemon=True).start()
    # Lanza el listener de la hotkey
    hotkey_listener()
