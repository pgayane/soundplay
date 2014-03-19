import numpy as np
import scipy.io.wavfile as wav
import sys
import pyaudio


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
