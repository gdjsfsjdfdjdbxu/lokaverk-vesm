"""
DIYables_MicroPython_OLED_SSD1309
MicroPython library for SSD1309-based monochrome OLED displays (I2C).

Supports 128x64, 128x32, 96x16, 64x48, 64x32 display sizes.
Extends framebuf.FrameBuffer for full drawing-primitive support.

Product page: https://diyables.io/products/2.4-inch-oled-display-module-ssd1309-128x64
Author: DIYables
License: MIT
"""

import framebuf
import time

# ---------------------------------------------------------------------------
# Pixel colour constants (0 = off, 1 = on)
# ---------------------------------------------------------------------------
PIXEL_OFF     = 0
PIXEL_ON      = 1
PIXEL_INVERSE = 2   # only meaningful for fill(); individual pixels toggle

# ---------------------------------------------------------------------------
# VCC-source selection
# ---------------------------------------------------------------------------
EXTERNALVCC  = 0x01   # External display voltage source
SWITCHCAPVCC = 0x02   # Generate display voltage from 3.3 V internally

# ---------------------------------------------------------------------------
# SSD1309 command constants (internal use)
# ---------------------------------------------------------------------------
_MEMORYMODE          = 0x20
_COLUMNADDR          = 0x21
_PAGEADDR            = 0x22
_SETCONTRAST         = 0x81
_CHARGEPUMP          = 0x8D
_SEGREMAP            = 0xA0
_DISPLAYALLON_RESUME = 0xA4
_NORMALDISPLAY       = 0xA6
_INVERTDISPLAY       = 0xA7
_SETMULTIPLEX        = 0xA8
_DISPLAYOFF          = 0xAE
_DISPLAYON           = 0xAF
_COMSCANDEC          = 0xC8
_SETDISPLAYOFFSET    = 0xD3
_SETDISPLAYCLOCKDIV  = 0xD5
_SETPRECHARGE        = 0xD9
_SETCOMPINS          = 0xDA
_SETVCOMDETECT       = 0xDB
_SETSTARTLINE        = 0x40
_DEACTIVATE_SCROLL   = 0x2E
_ACTIVATE_SCROLL     = 0x2F
_RIGHT_HORIZ_SCROLL  = 0x26
_LEFT_HORIZ_SCROLL   = 0x27
_VERT_RIGHT_SCROLL   = 0x29
_VERT_LEFT_SCROLL    = 0x2A
_SET_VERT_SCROLL_AREA = 0xA3


class OLED_SSD1309(framebuf.FrameBuffer):
    """
    Driver for SSD1309-based I2C OLED displays.

    Inherits from framebuf.FrameBuffer, so all MicroPython drawing primitives
    (pixel, fill, fill_rect, rect, line, hline, vline, text, blit, scroll, ...)
    are available without any extra imports.

    Basic usage::

        from machine import I2C, Pin
        from DIYables_MicroPython_OLED_SSD1309 import OLED_SSD1309

        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400_000)
        oled = OLED_SSD1309(128, 64, i2c)

        oled.fill(0)
        oled.text("Hello, World!", 0, 0)
        oled.show()
    """

    def __init__(self, width, height, i2c, addr=0x3C, rst=None,
                 vcc=SWITCHCAPVCC):
        """
        Initialise the SSD1309 OLED driver.

        :param width:   Display width in pixels (e.g. 128).
        :param height:  Display height in pixels (e.g. 64 or 32).
        :param i2c:     machine.I2C (or SoftI2C) instance.
        :param addr:    7-bit I2C address (default 0x3C).
        :param rst:     Optional machine.Pin object for hardware reset
                        (pass None if the reset pin is not wired).
        :param vcc:     SWITCHCAPVCC (default) or EXTERNALVCC.
        """
        self._width  = width
        self._height = height
        self._i2c    = i2c
        self._addr   = addr
        self._rst    = rst
        self._vcc    = vcc
        self._contrast = 0xCF

        # Allocate one contiguous buffer:
        #   byte 0       = I2C data-mode control byte (0x40, never changes)
        #   bytes 1..end = framebuffer (1 bit/pixel, MONO_VLSB layout)
        # This lets show() send the entire block in one writeto() call with
        # no temporary allocations and no data copy.
        _fb_size = width * ((height + 7) // 8)
        self._data_buf = bytearray(1 + _fb_size)
        self._data_buf[0] = 0x40                      # data control byte
        _fb_view = memoryview(self._data_buf)[1:]     # view into fb region

        # Initialise FrameBuffer using the view so drawings go into _data_buf
        super().__init__(_fb_view, width, height, framebuf.MONO_VLSB)

        self._init_display()

    # -----------------------------------------------------------------------
    # Low-level I2C helpers
    # -----------------------------------------------------------------------

    def _cmd(self, cmd):
        """Send a single command byte to the display."""
        self._i2c.writeto(self._addr, bytes([0x00, cmd]))

    def _cmd_list(self, cmds):
        """
        Send a sequence of command bytes in one I2C transaction.

        Control byte 0x00 (Co=0, D/C#=0) causes the SSD1309 to interpret all
        subsequent bytes in the same transaction as command bytes.
        """
        buf = bytearray(1 + len(cmds))
        buf[0] = 0x00
        buf[1:] = bytearray(cmds)
        self._i2c.writeto(self._addr, buf)

    # -----------------------------------------------------------------------
    # Initialisation
    # -----------------------------------------------------------------------

    def _init_display(self):
        """Perform hardware reset (if pin provided) and run init sequence."""

        # Hardware reset
        if self._rst is not None:
            self._rst.value(1)
            time.sleep_ms(1)
            self._rst.value(0)
            time.sleep_ms(10)
            self._rst.value(1)
            time.sleep_ms(10)

        # Determine COM-pins config and contrast based on resolution
        com_pins = 0x12
        self._contrast = 0xCF

        w, h = self._width, self._height
        ext = (self._vcc == EXTERNALVCC)

        if   w == 128 and h == 64:
            com_pins   = 0x12
            self._contrast = 0x9F if ext else 0xCF
        elif w == 128 and h == 32:
            com_pins   = 0x02
            self._contrast = 0x8F
        elif w == 96  and h == 16:
            com_pins   = 0x02
            self._contrast = 0x10 if ext else 0xAF
        elif w == 64  and h == 48:
            com_pins   = 0x12
            self._contrast = 0x9F if ext else 0xCF
        elif w == 64  and h == 32:
            com_pins   = 0x12
            self._contrast = 0x10 if ext else 0xCF

        precharge = 0x22 if ext else 0xF1
        charge    = 0x10 if ext else 0x14

        self._cmd_list([
            _DISPLAYOFF,
            _SETDISPLAYCLOCKDIV, 0x80,          # suggested ratio
            _SETMULTIPLEX,       h - 1,
            _SETDISPLAYOFFSET,   0x00,           # no offset
            _SETSTARTLINE | 0x00,               # start line 0
            _CHARGEPUMP,         charge,         # compatibility byte
            _MEMORYMODE,         0x00,           # horizontal addressing
            _SEGREMAP | 0x01,                   # col 127 -> SEG0
            _COMSCANDEC,                        # scan COM[N-1] -> COM0
            _SETCOMPINS,         com_pins,
            _SETCONTRAST,        self._contrast,
            _SETPRECHARGE,       precharge,
            _SETVCOMDETECT,      0x40,
            _DISPLAYALLON_RESUME,               # output follows RAM
            _NORMALDISPLAY,                     # non-inverted
            _DEACTIVATE_SCROLL,
            _DISPLAYON,
        ])

    # -----------------------------------------------------------------------
    # Core display operations
    # -----------------------------------------------------------------------

    def show(self):
        """
        Push the framebuffer contents to the physical display.

        Call this after every series of drawing operations to make them
        visible.
        """
        x0 = 32 if self._width == 64 else 0
        x1 = x0 + self._width - 1

        self._cmd_list([
            _PAGEADDR,   0,    0xFF,  # page 0 .. last
            _COLUMNADDR, x0,   x1,   # column range
        ])

        # _data_buf[0] == 0x40 (already set); [1:] is the live framebuffer
        self._i2c.writeto(self._addr, self._data_buf)

    def clear(self):
        """Clear the framebuffer (all pixels off). Call show() to update."""
        self.fill(0)

    # -----------------------------------------------------------------------
    # Hardware display settings
    # -----------------------------------------------------------------------

    def invert(self, invert):
        """
        Invert display colours at the hardware level.

        :param invert: True = inverted (pixels on where buffer is 0),
                       False = normal.
        """
        self._cmd(_INVERTDISPLAY if invert else _NORMALDISPLAY)

    def dim(self, dim):
        """
        Dim the display by dropping contrast to zero, or restore.

        :param dim: True = dim (contrast 0), False = restore saved contrast.
        """
        self._cmd(_SETCONTRAST)
        self._cmd(0 if dim else self._contrast)

    def set_contrast(self, contrast):
        """
        Set display contrast.

        :param contrast: Integer 0–255.
        """
        self._contrast = contrast & 0xFF
        self._cmd(_SETCONTRAST)
        self._cmd(self._contrast)

    def poweroff(self):
        """Put the display into sleep mode (display off, RAM retained)."""
        self._cmd(_DISPLAYOFF)

    def poweron(self):
        """Wake the display from sleep mode."""
        self._cmd(_DISPLAYON)

    # -----------------------------------------------------------------------
    # Hardware scroll
    # -----------------------------------------------------------------------

    def scroll_right(self, start=0x00, stop=0x07):
        """
        Start continuous horizontal scroll to the right.

        :param start: First page (row-group) to scroll (0–7).
        :param stop:  Last  page (row-group) to scroll (0–7).
        """
        self._cmd_list([
            _RIGHT_HORIZ_SCROLL, 0x00, start, 0x00, stop,
            0x00, 0xFF, _ACTIVATE_SCROLL,
        ])

    def scroll_left(self, start=0x00, stop=0x07):
        """
        Start continuous horizontal scroll to the left.

        :param start: First page to scroll (0–7).
        :param stop:  Last  page to scroll (0–7).
        """
        self._cmd_list([
            _LEFT_HORIZ_SCROLL, 0x00, start, 0x00, stop,
            0x00, 0xFF, _ACTIVATE_SCROLL,
        ])

    def scroll_diag_right(self, start=0x00, stop=0x07):
        """
        Start continuous diagonal (vertical + right) scroll.

        :param start: First page to scroll (0–7).
        :param stop:  Last  page to scroll (0–7).
        """
        self._cmd_list([
            _SET_VERT_SCROLL_AREA, 0x00, self._height,
            _VERT_RIGHT_SCROLL, 0x00, start, 0x00, stop, 0x01,
            _ACTIVATE_SCROLL,
        ])

    def scroll_diag_left(self, start=0x00, stop=0x07):
        """
        Start continuous diagonal (vertical + left) scroll.

        :param start: First page to scroll (0–7).
        :param stop:  Last  page to scroll (0–7).
        """
        self._cmd_list([
            _SET_VERT_SCROLL_AREA, 0x00, self._height,
            _VERT_LEFT_SCROLL, 0x00, start, 0x00, stop, 0x01,
            _ACTIVATE_SCROLL,
        ])

    def stop_scroll(self):
        """Stop any active hardware scrolling."""
        self._cmd(_DEACTIVATE_SCROLL)

    # -----------------------------------------------------------------------
    # Buffer access helpers
    # -----------------------------------------------------------------------

    def get_pixel(self, x, y):
        """
        Read a pixel value from the framebuffer.

        :returns: 1 if the pixel is on, 0 if off, or -1 if out of bounds.
        """
        if 0 <= x < self._width and 0 <= y < self._height:
            fb = memoryview(self._data_buf)[1:]  # framebuffer region
            return (fb[x + (y // 8) * self._width] >> (y & 7)) & 1
        return -1

    def get_buffer(self):
        """Return a memoryview of the raw framebuffer (without control byte)."""
        return memoryview(self._data_buf)[1:]

    def command(self, cmd):
        """Send a raw SSD1309 command byte."""
        self._cmd(cmd)
