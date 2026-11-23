"""Read a tap recording (WAV) and report the strongest peaks and their damping.

Standard library only. Usage:
    python3 -I tap_analyze.py tap.wav            # list peaks 50-8000 Hz
    python3 -I tap_analyze.py tap.wav 305        # track the peak nearest 305 Hz

What it prints for each peak:
    f      peak frequency, Hz (parabolic interpolation on the spectrum)
    eta    loss factor from the ring-down slope (eta = 2.2 / (f * T60))
    T60    time to decay 60 dB, s (extrapolated from the fitted slope)
    fit    dB range actually fitted; under 15 dB means the number is weak

Record mono or stereo, 44.1 or 48 kHz, one tap per file, start the file
just before the tap. Use the first channel.
"""
import cmath
import math
import struct
import sys
import wave


def read_wav(path):
    with wave.open(path, "rb") as w:
        n, ch, sw, fs = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    if sw == 2:
        data = struct.unpack("<%dh" % (n * ch), raw)
        scale = 32768.0
    elif sw == 3:
        data = [int.from_bytes(raw[i:i + 3], "little", signed=True) for i in range(0, len(raw), 3)]
        scale = 8388608.0
    elif sw == 4:
        data = struct.unpack("<%di" % (n * ch), raw)
        scale = 2147483648.0
    else:
        raise SystemExit("unsupported sample width")
    return [data[i] / scale for i in range(0, len(data), ch)], fs


def fft(x):
    n = len(x)
    if n == 1:
        return x
    even, odd = fft(x[0::2]), fft(x[1::2])
    out = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * odd[k]
        out[k], out[k + n // 2] = even[k] + t, even[k] - t
    return out


def goertzel_env(x, fs, f, frame):
    """Amplitude at frequency f in successive frames (hop = frame/4)."""
    w = 2 * math.pi * f / fs
    c = 2 * math.cos(w)
    hann = [0.5 - 0.5 * math.cos(2 * math.pi * i / (frame - 1)) for i in range(frame)]
    env, times = [], []
    hop = frame // 4
    for start in range(0, len(x) - frame, hop):
        s1 = s2 = 0.0
        for i in range(frame):
            s0 = x[start + i] * hann[i] + c * s1 - s2
            s2, s1 = s1, s0
        p = s1 * s1 + s2 * s2 - c * s1 * s2
        env.append(math.sqrt(max(p, 1e-30)))
        times.append((start + frame / 2) / fs)
    return times, env


def decay(x, fs, f, frame_s=None):
    # frame: about 30 cycles, so neighbouring peaks are separated; then shortened
    # if the decay turns out to be fast compared with the frame
    if frame_s is None:
        frame_s = min(0.25, max(0.01, 30.0 / f))
    frame = int(fs * frame_s)
    t, env = goertzel_env(x, fs, f, frame)
    db = [20 * math.log10(e) for e in env]
    i0 = max(range(len(db)), key=lambda i: db[i])
    tail = sorted(db[len(db) * 4 // 5:])
    floor = tail[len(tail) // 2]  # median level of the last fifth = noise floor
    # fit the contiguous ring-down from 3 dB below the peak to 10 dB above the floor
    pts = []
    for i in range(i0, len(db)):
        if db[i] < floor + 10:
            break
        if db[i] <= db[i0] - 3:
            pts.append((t[i], db[i]))
    if len(pts) < 4:
        return None
    n = len(pts)
    mt = sum(p[0] for p in pts) / n
    md = sum(p[1] for p in pts) / n
    slope = sum((p[0] - mt) * (p[1] - md) for p in pts) / sum((p[0] - mt) ** 2 for p in pts)
    if slope >= 0:
        return None
    t60 = -60.0 / slope
    if t60 < 6 * frame_s and frame_s > 0.004:
        return decay(x, fs, f, frame_s / 2)
    return {"T60": t60, "eta": 2.2 / (f * t60), "fit_dB": pts[0][1] - pts[-1][1]}


def main():
    x, fs = read_wav(sys.argv[1])
    target = float(sys.argv[2]) if len(sys.argv) > 2 else None
    i0 = max(range(len(x)), key=lambda i: abs(x[i]))
    seg = x[i0:]
    nfft = 1
    while nfft < min(len(seg), 1 << 16):
        nfft <<= 1
    seg_f = seg[:nfft] + [0.0] * (nfft - len(seg[:nfft]))
    spec = [abs(v) for v in fft([complex(v) for v in seg_f])[: nfft // 2]]
    df = fs / nfft
    peaks = []
    for k in range(2, len(spec) - 2):
        f = k * df
        if 50 <= f <= 8000 and spec[k] > spec[k - 1] and spec[k] >= spec[k + 1] and spec[k] > spec[k - 2] and spec[k] >= spec[k + 2]:
            a, b, c = (math.log(max(spec[k + j], 1e-30)) for j in (-1, 0, 1))
            off = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
            peaks.append(((k + off) * df, spec[k]))
    if target:
        peaks = [min(peaks, key=lambda p: abs(p[0] - target))]
    else:
        big = max(p[1] for p in peaks)
        peaks = [p for p in peaks if p[1] > big * 10 ** (-30 / 20)]  # within 30 dB of the strongest
        peaks = sorted(peaks, key=lambda p: -p[1])[:6]
        peaks.sort()
    top = max(p[1] for p in peaks)
    print("    f (Hz)   level (dB)     eta      T60 (s)   fit (dB)")
    for f, a in peaks:
        d = decay(x, fs, f)
        lvl = 20 * math.log10(a / top)
        if d:
            print(f"{f:10.1f} {lvl:10.1f} {d['eta']:10.4f} {d['T60']:10.2f} {d['fit_dB']:9.1f}")
        else:
            print(f"{f:10.1f} {lvl:10.1f}       (decay too short or too noisy to fit)")


if __name__ == "__main__":
    main()
