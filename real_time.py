import pyaudio
import numpy as np
import scipy.io.wavfile as wav
import sys, struct
from ctypes import *
from contextlib import contextmanager
import wave
import time
from pitchshift_fft import *


stream = None
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

def start_speaker_stream():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    output=True)

def play(data):
    if stream is None:
        start_speaker_stream()

    stream.write(data)

def callback(in_data, frame_count, time_info, status):
    frames = list(chunks(unpack(in_data), frame_count))
    play(frames)

    return (in_data, pyaudio.paContinue)

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def unpack(buffer):
    return unpack_buffer(list(chunks(buffer, 2)))

def unpack_buffer(buffer):
    return [struct.unpack('h', frame)[0] for frame in buffer]

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

    chunk = 1024
    data = in_stream.read(chunk)
    while data != '':
        data = unpack(data)

        data = shift(data, shift_left, 10)

        data = [struct.pack('h', i) for i in data]
        data = ''.join(data)
        out_stream.write(data)
        data = in_stream.read(chunk)

    # in_stream.start_stream()
    # while in_stream.is_active():
    #     time.sleep(0.1)

    in_stream.stop_stream()
    in_stream.close()

    # stream.stop_stream()
    # stream.close()

    p.terminate()

if __name__ == "__main__":

    func = sys.argv[1]

    if func == 'play':
        filepath = sys.argv[2]
        play_audio(filepath)
    elif func == 'mic':
        capture_mic()

