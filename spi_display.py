import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image
import glob

# ---------------- PINS ----------------
DC = 24
RST = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)

# ---------------- SPI ----------------
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 20000000

# ---------------- LOW LEVEL ----------------
def cmd(c):
    """Send a single command byte to the display controller.

    Args:
        c (int): Register or command byte written with the D/C pin low.

    Returns:
        None: Updates the GPIO control line and writes one byte over SPI.
    """

    GPIO.output(DC, 0)
    spi.writebytes([c])

def data16(d):
    """Send one 16-bit data value to the display controller.

    Args:
        d (int): Unsigned 16-bit value split into high and low bytes.

    Returns:
        None: Updates the GPIO control line and writes two bytes over SPI.
    """

    GPIO.output(DC, 1)
    spi.writebytes([d >> 8, d & 0xFF])

def write_reg(reg, val):
    """Write a 16-bit value into a display controller register.

    Args:
        reg (int): Register address or command byte.
        val (int): 16-bit register payload written after the register select.

    Returns:
        None: Delegates to `cmd()` and `data16()` to transmit the register
        update.
    """

    cmd(reg)
    data16(val)

def reset():
    """Pulse the display reset pin to force the controller into a clean state.

    Returns:
        None: Drives the reset GPIO low then high with short timing delays.
    """

    GPIO.output(RST, 0)
    time.sleep(0.1)
    GPIO.output(RST, 1)
    time.sleep(0.1)

# ---------------- INIT ----------------
def init_display():
    """Initialize the display controller registers for normal operation.

    Returns:
        None: Resets the panel and writes the register sequence required to
        power up the display and enable drawing.
    """

    reset()

    write_reg(0x01, 0x011C)
    write_reg(0x02, 0x0100)
    write_reg(0x03, 0x1030)
    write_reg(0x08, 0x0808)
    write_reg(0x0C, 0x0000)
    write_reg(0x0F, 0x0A01)

    write_reg(0x20, 0x0000)
    write_reg(0x21, 0x0000)

    write_reg(0x10, 0x0A00)
    write_reg(0x11, 0x1038)
    write_reg(0x12, 0x1121)
    write_reg(0x13, 0x0066)
    write_reg(0x14, 0x5F60)

    time.sleep(0.1)

    write_reg(0x30, 0x0000)
    write_reg(0x31, 0x00DB)
    write_reg(0x32, 0x0000)
    write_reg(0x33, 0x0000)
    write_reg(0x34, 0x00DB)
    write_reg(0x35, 0x0000)

    write_reg(0x50, 0x0000)
    write_reg(0x51, 0x0808)
    write_reg(0x52, 0x080A)
    write_reg(0x53, 0x000A)
    write_reg(0x54, 0x0A08)
    write_reg(0x55, 0x0808)
    write_reg(0x56, 0x0000)
    write_reg(0x57, 0x0A00)
    write_reg(0x58, 0x0710)
    write_reg(0x59, 0x0710)

    write_reg(0x07, 0x1017)  # DISPLAY ON

# ---------------- WINDOW ----------------
def set_window(x1, y1, x2, y2):
    """Configure the rectangular drawing window used for subsequent pixel data.

    Args:
        x1 (int): Left column index of the drawing region.
        y1 (int): Top row index of the drawing region.
        x2 (int): Right column index of the drawing region.
        y2 (int): Bottom row index of the drawing region.

    Returns:
        None: Programs the controller window registers and prepares RAM writes.
    """

    write_reg(0x36, x2)
    write_reg(0x37, x1)
    write_reg(0x38, y2)
    write_reg(0x39, y1)
    write_reg(0x20, x1)
    write_reg(0x21, y1)
    cmd(0x22)

# ---------------- FAST IMAGE DISPLAY ----------------
def display_image_fast(image_path):
    """Load an image, convert it to RGB565 bytes, and stream it to the display.

    Args:
        image_path (str): Path to the image file opened with Pillow.

    Returns:
        None: Resizes the image to `176x220`, converts each pixel to RGB565,
        and writes the frame buffer to the display in SPI chunks.
    """

    img = Image.open(image_path).convert("RGB")
    img = img.resize((176, 220))

    set_window(0, 0, 175, 219)
    GPIO.output(DC, 1)

    pixels = img.load()

    buffer = []

    for y in range(220):
        for x in range(176):
            r, g, b = pixels[x, y]
            color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buffer.append(color >> 8)
            buffer.append(color & 0xFF)

    # 🔥 SEND IN CHUNKS (fix)
    CHUNK_SIZE = 4096 #CHUNK_SIZE = 2048
    
    for i in range(0, len(buffer), CHUNK_SIZE):
        spi.writebytes(buffer[i:i+CHUNK_SIZE])

# ---------------- VIDEO PLAYER ----------------
def play_frames(folder=".", fps=10):
    """Play sequential JPEG frames from a folder at a target frame rate.

    Args:
        folder (str): Directory containing files that match `frame_*.jpg`.
        fps (int | float): Target playback rate used to compute frame delay.

    Returns:
        None: Streams each discovered frame to the display and sleeps as needed
        to approximate the requested frame rate.
    """

    frame_delay = 4.0 / fps

    frames = sorted(glob.glob(f"{folder}/frame_*.jpg"))

    print(f"Playing {len(frames)} frames at {fps} FPS")

    for frame in frames:
        start = time.time()

        display_image_fast(frame)

        elapsed = time.time() - start
        time.sleep(max(0, frame_delay - elapsed))

# ---------------- MAIN ----------------
init_display()

# change folder if needed
play_frames(folder=".", fps=10)
