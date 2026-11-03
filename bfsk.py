"""
Shared settings and helpers for the transmitter and the receiver.
Change the settings HERE so both sides always agree.
"""
import numpy as np

# ---------------- Settings ----------------
MESSAGE     = "TEST"    # word to send
MAX_CHARS   = 4         # fixed message length, so the receiver knows how many bits to read
DELTA_ALPHA = 0.1       # how much to change the alpha channel for each bit (0.0 = no flicker, 1.0 = full flicker)
F0          = 5         # flicker frequency (Hz) for bit 0
F1          = 10        # flicker frequency (Hz) for bit 1
BIT_TIME    = 0.2       # seconds per bit -> data rate = 1 / BIT_TIME bits per second
LEAD_TIME   = 1.0       # seconds of steady image between repeats of the message
PREAMBLE    = "10110001"  # known pattern the receiver uses to find where data starts


# Helpers
def text_to_bits(text):
    text = text[:MAX_CHARS].ljust(MAX_CHARS)
    return "".join(format(ord(c), "08b") for c in text)


def bits_to_text(bits):
    chars = [chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits) - 7, 8)]
    return "".join(c if 32 <= ord(c) < 127 else "?" for c in chars)


def level(bits, t):
    """Square wave value (1 = high alpha, 0 = low alpha) at time t seconds
    after the first bit starts. Each bit flickers at F0 (bit 0) or F1 (bit 1)."""
    k = min(int(t // BIT_TIME), len(bits) - 1)
    tau = t - k * BIT_TIME
    f = F1 if bits[k] == "1" else F0
    return 1 if np.sin(2 * np.pi * f * tau) >= 0 else 0
