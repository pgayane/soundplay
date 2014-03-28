import numpy as np
import scipy.io.wavfile as wav
import sys
import pyaudio
from scipy import *


def shift_pv(signalin, tscale):
    ''' takes signalin which should be composition of two chunks size
        where the second will be repeted for the next call '''
    L = len(signalin)
    N = L/2
    H = N/2

    # if it is stero convert to mono
    # signalin = [signalin[i][0] for i in range(L)]


    # signal blocks for processing and output
    phi  = zeros(N)
    out = zeros(N, dtype=complex)
    sigout = zeros(L/tscale+N)

    # max input amp, window
    amp = max(signalin)
    win = hanning(N)
    p = 0
    pp = 0

    while p < L-(N+H):
        print p, L, H, tscale
        # take the spectra of two consecutive windows
        p1 = int(p)
        spec1 = fft(win*signalin[p1:p1+N])
        spec2 = fft(win*signalin[p1+H:p1+N+H])

        # take their phase difference and integrate
        phi += (angle(spec2) - angle(spec1))
        out.real, out.imag = cos(phi), sin(phi)

        # inverse FFT and overlap-add
        sigout[pp:pp+N] += win*ifft(abs(spec2)*out)
        pp += H
        p += H*tscale

    # return middle chunk
    print len(sigout), max(signalin), min(signalin)
    return  sigout
    # return (amp*sigout/max(sigout))[(L/4)*(3/4):(L/4)*(3/4) + L/4]

def shift(data, shift_func, shift_size = 50):
    fft_data = np.fft.rfft(data)

    shifted = shift_func(fft_data, shift_size)
    new_data = np.fft.irfft(shifted).real
    data_out = np.array(new_data, dtype='int16')
    return data_out

def shift_right(fft_data, shift_size = 50):
    l = len(fft_data)

    return np.concatenate((fft_data[l-shift_size:l] , \
                        fft_data[:l-shift_size]))

def shift_left(fft_data, shift_size = 50):
    l = len(fft_data)
    return np.concatenate((fft_data[shift_size:l] , \
                        [0. + 0.j for i in range(shift_size)]))


def main(filepath, new_filepath, shift_func, shift_size = 50):
    sr, data  = wav.read(filepath)

    shifted = shift(data, shift_func, shift_size)

    wav.write(new_filepath, sr, np.array(shifted, dtype='int16'))

if __name__ == '__main__':
    filepath = sys.argv[1]
    new_filepath = sys.argv[2]
    shift_dir = sys.argv[3]
    if shift_dir == 'left':
        shift_func = shift_left
    else:
        shift_func = shift_right

    shift_size = 50
    if len(sys.argv) > 4:
        shift_size = int(sys.argv[4])

    main(filepath, new_filepath, shift_func, shift_size)
