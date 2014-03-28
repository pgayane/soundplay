import sys
from scipy import *
from scipy.io import wavfile
import numpy as np

def pv_file(filein, fileout):
  (sr, signalin) = open_wav(filein)
  sigout = pv_signal(signalin, 2048, 512, float(1))
  write_wav(fileout, sigout, sr)

def open_wav(filepath):
  # read input and get the timescale factor
  (sr,signalin) = wavfile.read(filepath)
  signalin = [d[0] for d in signalin]
  return (sr, signalin)


def write_wav(filename, sigout, sr):
  #  write file to output, scaling it to original amp
  wavfile.write(filename,sr,array(sigout, dtype='int16'))


def pv_signal(signalin, chunk_size, step_size, tscale):

  N = chunk_size
  H = step_size

  L = len(signalin)
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

    # take the spectra of two consecutive windows
    p1 = int(p)
    spec1 =  fft(win*signalin[p1:p1+N])
    spec2 =  fft(win*signalin[p1+H:p1+N+H])

    # take their phase difference and integrate
    phi += (angle(spec2) - angle(spec1))
    out.real, out.imag = cos(phi), sin(phi)

    # inverse FFT and overlap-add
    sigout[pp:pp+N] += win*ifft(abs(spec2)*out)
    pp += H
    p += H*tscale

  return amp*sigout/max(sigout)

def try_partially(signalin, chunk_number):
  l = len(signalin)
  s = l/chunk_number

  sigout = pv_signal(signalin[:s], 2048, 512, float(1))
  for i in range(1, chunk_number):
    print i
    sigout = np.concatenate((sigout, pv_signal(signalin[i*s:(i+1)*s], 2048, 512, float(1))))
  return sigout

def pv_sequential(signalin, chunk_size, step_size, tscale):
  N = chunk_size
  H = step_size

  L = len(signalin)
  # signal blocks for processing and output
  phi  = zeros(N)
  out = zeros(N, dtype=complex)
  sigout = zeros(L/tscale+N)

  # max input amp, window
  amp = max(signalin)
  win = hanning(N)

  pp = 0
  s = L/50
  signal = signalin[:s]
  i  = 0
  while pp < L:
    p = 0
    print i, pp, s
    while p < s-(N+H) and pp < L:

      # take the spectra of two consecutive windows
      p1 = int(p)
      spec1 =  fft(win*signal[p1:p1+N])
      spec2 =  fft(win*signal[p1+H:p1+N+H])

      # take their phase difference and integrate
      phi += (angle(spec2) - angle(spec1))
      out.real, out.imag = cos(phi), sin(phi)

      # inverse FFT and overlap-add
      sigout[pp:pp+N] += win*ifft(abs(spec2)*out)
      pp += H
      p += H*tscale

    i+=1
    signal = signalin[i*(s-(N+H)): i*(s-(N+H)) + s]
    if len(signal)< s:
      print 'break'
      break

  print pp+N, len(sigout)
  return amp*sigout/max(sigout)

def try_partially_fromfile(filein, fileout):
  (sr, signalin) = open_wav(filein)
  sigout = try_partially(signalin, 50)
  write_wav(fileout, sigout, sr)

def try_sequental(filein, fileout):
  (sr, signalin) = open_wav(filein)
  sigout = pv_sequential(signalin, 2048, 512, float(1))
  write_wav(fileout, sigout, sr)

if __name__ == '__main__':
  try_sequental('fft_test.wav', 'pv_seq_test.wav')
