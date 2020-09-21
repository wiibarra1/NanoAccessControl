#!/usr/bin/python3

import aubio
import numpy as num
import pyaudio
import wave
import subprocess
import sys
import os
import time
import threading

# PyAudio object.
p = pyaudio.PyAudio()

# Open stream.
stream = p.open(format=pyaudio.paFloat32,
    channels=1, rate=44100, input=True,
    frames_per_buffer=1024)

# Initialize variables
pitch_total = []
target_pitch = []

# This function clears out target_pitch every 10 seconds to limit false positive
# tone identifications
def clear():
    threading.Timer(10, clear).start()
    del target_pitch[:]

clear()

# Aubio's pitch detection.
pDetection = aubio.pitch("default", 2048,
    2048//2, 44100)
# Set unit.
pDetection.set_unit("Hz")
pDetection.set_silence(-40)

while True:

    data = stream.read(1024)
    samples = num.fromstring(data,
        dtype=aubio.float_type)
    pitch = pDetection(samples)[0]
    # Compute the energy (volume) of the
    # current frame.
    volume = num.sum(samples**2)/len(samples)
    # Format the volume output so that at most
    # it has six decimal numbers.

    # This listens for a set frequency
    volume = "{:.6f}".format(volume)
    if len(pitch_total) < 100:
        pitch_total.append(pitch)
    else:
        del pitch_total[:]
    for v in pitch_total:
        # Change the frequency it listens for here  
        if 399 < v < 401:
            if v not in target_pitch:
                target_pitch.append(v)
    if len(target_pitch) > 20:
        # This quits the script and launches face_recognize.py.  Change directory.
        subprocess.run("/home/william/face_recognize.py")
        sys.exit()
    print(pitch)
    print(target_pitch)
