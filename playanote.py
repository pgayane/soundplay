#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scipy.io.wavfile as wav
from numpy import *

sine  = lambda f, t: math.sin(2 * math.pi * t * f / 44100.0)

if __name__ == "__main__":
    
    data = []
    samplerate = 44100
    freq_high = 500
    freq_low = 300

    note1 = sine(freq_high, 1)
    note2 = sine(freq_low, 1)

    volumn = 50 / 100.0 * 32760
    for i in range(20000):
        data.append(int(sine(freq_high, i)*volumn))
    for i in range(20000): 
        data.append(int(sine(freq_low, i)*volumn))
    
    wav.write("anote.wav", samplerate, array(data, dtype=int16))
    