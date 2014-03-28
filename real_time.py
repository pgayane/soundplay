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
from scipy import *



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
        data[i] /= 2
    return data

def reduce_noise(data):
    threshold = 0.005

    amplitude = get_rms(data)

    if amplitude < threshold:
        data = reduce(data)
    return data

def capture_mic():
    tscale = 1.0
    p = pyaudio.PyAudio()

    in_stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    input = True)
    out_stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=int(44100*tscale),
                    output=True)

    data_to_file = []

    chunk = 512
    prev_data = []
    data = []
    after_data = in_stream.read(chunk)

    for i in range(300):

        after_data = utils.unpack(after_data)
        # after_data = reduce_noise(after_data)

        if prev_data != []:
            concat = np.concatenate(
                                        ((
                                            np.concatenate(((prev_data,data))),after_data
                                        ))
                                    )
            shifted_data = shift_pv(concat, tscale)

        #     data_to_file.extend(shift_data)

            data_out = utils.pack(shifted_data)

            data_out = ''.join(data_out)
            out_stream.write(data_out)

        prev_data = data
        data = after_data
        after_data = in_stream.read(chunk)

    in_stream.stop_stream()
    in_stream.close()

    out_stream.stop_stream()
    out_stream.close()
    wav.write('test.wav',44100*2, array(data_to_file, dtype='int16'))
    p.terminate()

def real_time_modify():
    tscale = 1.0
    p = pyaudio.PyAudio()

    in_stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    input = True)
    out_stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=int(44100*tscale),
                    output=True)

    chunk = 1024

    data = in_stream.read(chunk)
    data = utils.unpack(data)
    print 'data', len(data)

    next_data = in_stream.read(chunk)
    next_data = utils.unpack(next_data)

    amp = 0
    out_data = np.concatenate(([], zeros(chunk)))

    L = len(data)
    N = L/2
    H = N/2

    phi = zeros(N)
    out = zeros(N, dtype=complex)

    win = hanning(N)
    p = 0
    pp = 0

    for i in range(0,300):
        concat = np.concatenate(((data, next_data)))
        amp = max(amp, max(concat))

        out_data = np.concatenate((out_data, zeros(N/tscale)))
        p = 0
        for i in range(2):
            # take the spectra of two consecutive windows
            p1 = int(p)
            spec1 = fft(win*concat[p1:p1+N])
            spec2 = fft(win*concat[p1+H:p1+N+H])

            # take their phase difference and integrate
            phi += (angle(spec2) - angle(spec1))
            out.real, out.imag = cos(phi), sin(phi)

            # inverse FFT and overlap-add
            print 'pp:pp+N', pp, pp+N
            out_data[pp:pp+N] += win*ifft(abs(spec2)*out)
            pp += H
            p += H*tscale

        out_data = amp*out_data/max(out_data)

        out_formatted = utils.pack(out_data[i*chunk:(i+1)*chunk])
        out_formatted = ''.join(out_formatted)
        out_stream.write(out_formatted)

        data = next_data
        next_data = in_stream.read(chunk)
        next_data = utils.unpack(next_data)

    in_stream.stop_stream()
    in_stream.close()

    out_stream.stop_stream()
    out_stream.close()
    # wav.write('test.wav',44100*2, array(data_to_file, dtype='int16'))
    p.terminate()


if __name__ == "__main__":

    func = sys.argv[1]

    if func == 'play':
        filepath = sys.argv[2]
        play_audio(filepath)
    elif func == 'mic':
        real_time_modify()

