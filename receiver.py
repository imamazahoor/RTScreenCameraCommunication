"""
Receiver: reads the phone video of the screen, recovers the bits and the word,
and reports bit error rate and data rate.
"""
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from bfsk import *

video_path = sys.argv[1]
expected = sys.argv[2] if len(sys.argv) > 2 else None
FPS_OVERRIDE = None

# 1. Mean brightness of each frame
cap = cv2.VideoCapture(video_path)
fs = FPS_OVERRIDE or cap.get(cv2.CAP_PROP_FPS)
vals = []
while True:
    ok, frame = cap.read()
    if not ok:
        break
    vals.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean())
cap.release()
x = np.array(vals)
print(f"{len(x)} frames at {fs:.1f} fps")

# 2. Remove slow changes (auto-exposure, hand movement): subtract 1 s moving average
win = int(fs)
x = x - np.convolve(x, np.ones(win) / win, mode="same")

# 3. Find where the data starts by matching the known preamble
# samples per bit
spb = BIT_TIME * fs
t_pre = np.arange(int(len(PREAMBLE) * spb)) / fs
template = np.array([level(PREAMBLE, t) for t in t_pre], dtype=float)
template -= template.mean()

n_bits = 8 * MAX_CHARS
packet_len = int((len(PREAMBLE) + n_bits) * spb)
corr = np.correlate(x, template, mode="valid")
start = int(np.argmax(corr[: len(x) - packet_len]))
data_start = start + len(PREAMBLE) * spb

# 4. For each bit window, compare energy at F0 vs F1
bits = ""
for k in range(n_bits):
    a = int(round(data_start + k * spb))
    seg = x[a: a + int(spb)]
    tt = np.arange(len(seg)) / fs
    p0 = abs(np.sum(seg * np.exp(-2j * np.pi * F0 * tt)))
    p1 = abs(np.sum(seg * np.exp(-2j * np.pi * F1 * tt)))
    bits += "1" if p1 > p0 else "0"

print("Received bits:", bits)
print("Received text:", repr(bits_to_text(bits)))

# 5. Bit error rate and data rate
if expected:
    sent = text_to_bits(expected)
    correct = sum(s == r for s, r in zip(sent, bits))
    ber = 1 - correct / len(sent)
    rate = correct / (len(sent) * BIT_TIME)
    print(f"BER = {ber:.3f}   Data rate = {rate:.2f} bits/s")

# Plot the signal and where the data was found
t = np.arange(len(x)) / fs
plt.figure(figsize=(12, 3))
plt.plot(t, x, lw=0.8)
plt.axvline(start / fs, color="g", ls="--", label="Preamble start")
plt.axvline(data_start / fs, color="r", ls="--", label="Data start")
plt.xlabel("Time (s)"); plt.ylabel("Brightness (a.u.)")
plt.title(f"Received signal  (F0={F0} Hz, F1={F1} Hz, bit time={BIT_TIME}s, delta alpha={DELTA_ALPHA})")
plt.legend(); plt.tight_layout()
plt.savefig("received_signal.png", dpi=150)
plt.show()
