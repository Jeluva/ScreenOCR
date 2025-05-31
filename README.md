# ScreenOCR

**ScreenOCR** es una utilidad liviana en Python que permite extraer texto de cualquier área seleccionada de la pantalla con solo presionar un atajo de teclado. El texto reconocido queda automáticamente copiado al portapapeles para que puedas pegarlo donde lo necesites.

---

## Características

- 🎯 **Selección de región en pantalla:**  
  Al presionar `Shift + Alt + S`, aparece un recuadro semitransparente que puedes arrastrar para definir la zona de la pantalla a capturar.

- 🤖 **OCR con Tesseract:**  
  Utiliza [pytesseract](https://github.com/madmaze/pytesseract) y los datos de idioma de Tesseract para reconocer texto (por defecto en inglés, pero se puede configurar para otros idiomas).

- 📋 **Copia al portapapeles:**  
  Una vez extraído el texto, se copia automáticamente al portapapeles usando `pyperclip`.

- 💻 **Ícono en bandeja del sistema:**  
  Corre como aplicación en segundo plano con un ícono en la bandeja del sistema (system tray). Desde el menú del ícono, se puede cerrar la aplicación.

- 🔥 **Ligero y multiplataforma (Windows, especialmente):**  
  Diseñado con dependencias mínimas para que no sobrecargue el sistema. Requiere Windows (por el uso de APIs de captura de pantalla y DPI en Windows).

---

## Requisitos

- Python **3.6+**
- Sistema operativo: **Windows** (por el uso de `ctypes` y métricas de pantalla de Windows)
- Paquetes de Python:
  - `pillow`
  - `pytesseract`
  - `pyperclip`
  - `keyboard`
  - `pystray`
  - `mss`
- Instalación de **Tesseract OCR** (ejecutable y archivos tessdata):
  - Ruta por defecto de instalación (en Windows):  
    - Ejecutable: `C:\Program Files\Tesseract-OCR\tesseract.exe`
    - Datos de idioma (tessdata): `C:\Program Files\Tesseract-OCR\tessdata`

---

## Instalación

1. **Instalar Python 3.6+**  
   Asegúrate de tener Python instalado y agregado a la variable de entorno `PATH`.

2. **Instalar Tesseract OCR**  
   - Descarga el instalador desde la página oficial:  
     https://github.com/tesseract-ocr/tesseract  
   - Durante la instalación, toma nota de la ruta donde se instala (por defecto: `C:\Program Files\Tesseract-OCR\`).
   - Verifica que dentro de esa carpeta exista `tesseract.exe` y la subcarpeta `tessdata`.

3. **Clonar o descargar este proyecto**  
   ```bash
   git clone https://tu-repositorio/screenocr.git
   cd screenocr
