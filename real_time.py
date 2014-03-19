import pyaudio
import numpy as np
import scipy.io.wavfile as wav
import sys, struct
from ctypes import *
from contextlib import contextmanager
import wave
import time, math
from pitchshift_fft import *
import utils
from numpy import *


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


def play_audio(filepath):
    CHUNK = 1024
    wf = wave.open(filepath, 'rb')

    with noalsaerr():

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)


        data = wf.readframes(CHUNK)

        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)


        stream.stop_stream()
        stream.close()

        p.terminate()

def get_rms( data ):
       # iterate over the block.
    sum_squares = 0.0
    for sample in data:
        # sample is a signed short in +/- 32768.
        # normalize it to 1.0
        n = sample * (1.0/32768)
        sum_squares += n*n

    return math.sqrt( sum_squares / len(data) )

def reduce(data):
    for i in range(len(data)):
        data[i] =0
    return data

def reduce_noise(data):
    threshold = 0.005

    amplitude = get_rms(data)

    if amplitude < threshold:
        data = reduce(data)
    return data

def capture_mic():
    p = pyaudio.PyAudio()

    in_stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    input = True)
    out_stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    output=True)

    data_to_file = []
    chunk = 1024
    data = in_stream.read(chunk)
    # while data != '':
    for i in range(600):
        data = utils.unpack(data)
        data = reduce_noise(data)
        data = shift(data, shift_left, 5)

        data_to_file.extend(data)

        data = utils.pack(data)

        data = ''.join(data)

        out_stream.write(data)

        data = in_stream.read(chunk)

    in_stream.stop_stream()
    in_stream.close()

    out_stream.stop_stream()
    out_stream.close()
    wav.write('test.wav',44100*2, array(data_to_file, dtype='int16'))
    p.terminate()

if __name__ == "__main__":

    func = sys.argv[1]

    if func == 'play':
        filepath = sys.argv[2]
        play_audio(filepath)
    elif func == 'mic':
        capture_mic()

