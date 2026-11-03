# Real-Time Screen-Camera Communication Using the Alpha Channel

> This project is part of a course assignment for **17320: Machine Learning & Sensing for Healthcare @ CMU**.
> It is a simplified version of the system described in the following paper:
> Tianxing Li, Chuankai An, Xinran Xiao, Andrew T. Campbell, and Xia Zhou. **"Real-Time Screen-Camera Communication Behind Any Scene."** In *Proceedings of the 13th Annual International Conference on Mobile Systems, Applications, and Services (MobiSys '15)*, Florence, Italy, May 2015. DOI: [10.1145/2742647.2742667](https://doi.org/10.1145/2742647.2742667).

## Files

| File | What it does |
|---|---|
| `bfsk.py` | Shared settings (message, alpha difference, frequencies, bit time) and helper functions |
| `transmitter.py` | Shows the picture full-screen and flickers its alpha to send the message |
| `receiver.py` | Reads the phone video, finds the message, decodes the bits and prints the BER and data rate |

## Requirements

```
pip install numpy opencv-python matplotlib pygame
```

## How to run

1. **Choose settings** in `bfsk.py`:
   ```python
   MESSAGE     = "TEST"   # word to send (up to 4 characters)
   DELTA_ALPHA = 0.5      # alpha switches between 1.0 and 1.0 - DELTA_ALPHA
   BIT_TIME    = 0.4      # seconds per bit (0.4 = 2.5 bits/s, 0.2 = 5 bits/s)
   ```
2. **Start the transmitter** (press any key to stop):
   ```
   python transmitter.py cat_picture.jpg
   ```
3. **Record the screen with the phone** (30 fps, exposure locked, phone kept still).
   Record for at least 40 s when `BIT_TIME = 0.4`, or 20 s when `BIT_TIME = 0.2`.
4. **Decode the video** on the laptop. `bfsk.py` must have the same settings used while recording:
   ```
   python receiver.py video.mp4 TEST
   ```
   It prints the received text, the bit error rate (BER) and the data rate, and saves a plot of the signal as `received_signal.png`.
   **IMPORTANT**: This repository does not contain my videos due to size limits. To test, please record a video of your own.

## How it works

1. The transmitter sends a known 8-bit start pattern (preamble), then the message as 8 bits per character.
2. The receiver takes the average brightness of each video frame. A lower alpha makes the screen darker, so the flicker shows up as a brightness signal.
3. Slow brightness changes (camera auto-exposure, hand movement) are removed by subtracting a 1-second moving average.
4. The receiver finds the start of the message by matching the known preamble against the signal.
5. For each bit, it checks whether there is more 5 Hz or 10 Hz flicker, and picks bit 0 or bit 1.

Both frequencies must stay below half the camera's frame rate (15 Hz for 30 fps). To tell 5 Hz and 10 Hz apart, each bit must last at least 1/(10 − 5) = 0.2 s, so the fastest rate with a 30 fps camera is 5 bits/s.

## Results

Bit error rate (BER) and data rate for message "TEST":

| Δα | Bit time | 20 cm | 40 cm | 80 cm | 120 cm |
|---|---|---|---|---|---|
| 0.5 | 0.4 s | BER 0, 2.5 b/s | BER 0, 2.5 b/s | BER 0, 2.5 b/s | BER 0, 2.5 b/s |
| 0.1 | 0.4 s | BER 0, 2.5 b/s | BER 0, 2.5 b/s | BER 0, 2.5 b/s | BER 0, 2.5 b/s |
| 0.5 | 0.2 s | BER 0, 5 b/s | BER 0, 5 b/s | BER 0, 5 b/s | BER 0, 5 b/s |
| 0.1 | 0.2 s | BER 0, 5 b/s | BER 0.406, 2.97 b/s | BER 0.625, 1.88 b/s | BER 0.406, 2.97 b/s |

- At 2.5 bits/s, communication was error-free in every test.
- At 5 bits/s, it was error-free with Δα = 0.5 at all distances. With Δα = 0.1 it failed beyond 20 cm, because the flicker was too weak and the bits too short.
- The flicker was visible to the eye in all tests (fainter with Δα = 0.1), since 5-10 Hz is far below the ~50-60 Hz at which the eye stops noticing flicker.
