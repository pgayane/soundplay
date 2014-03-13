from numpy import *
import matplotlib.pyplot as pyplot

from scipy.io.wavfile import write
import wave, struct, random, math
import os, sys, subprocess


sine     = lambda f, t, sr: math.sin(2 * math.pi * t * f / sr)
square   = lambda f, t, sr: 0.6 * ((t % (sr / f) >= ((sr / f)/2)) * 2 - 1)
sawtooth = lambda f, t, sr: (t % (sr / f)) / (sr / f) * 2 - 1

class SoundPlay:

    def __int__(self):
        self.data = []
        self.sample_rate = 44100
        self.time = 0
        self.nframes = 0

    def get_wav_data(self, file):
        # open a file for writing
        infile = wave.open(file, 'r')

        self.nframes = infile.getnframes()
        self.sample_rate = infile.getframerate()
        self.time = self.nframes / self.sample_rate

        self.data = []
        for i in range(self.nframes):
            nextframe = infile.readframes(1)        
            
            # this returns C-style little-endian shorts, so we convert...
            self.data += struct.unpack('hh', nextframe)

        return self.data


    def make_wav(self, data, outfile, samplerate = 44100):
        wavfile = wave.open(outfile, 'w')
        params=(2, 2, samplerate, 0, 'NONE', 'not compressed')
        wavfile.setparams(params)
        
        # convert back to C-style little-endian shorts...
        converted = [struct.pack('h', i) for i in data]
        outdata = ''
        for i in converted:
            outdata += i[0]
            outdata += i[1]
        wavfile.writeframes(outdata)
        wavfile.close()


    def slow(self, filename):
        slow_data = []

        for d in self.data(0,len(self.data), 100):

            slow_data.append(d)
            slow_data.append(d)

        self.make_wav(slow_data, filename, self.sample_rate)
        # self.make_wav(self.data, filename, self.sample_rate/2)

    def fast(self, filename):
        # fast_data = []
        
        # for i in range(0,len(self.data),2):
        #     fast_data.append(self.data[i])

        # self.make_wav(fast_data, filename, self.sample_rate)
        self.make_wav(self.data, filename, self.sample_rate*2)

    def __str__(self):
        return str(self.sample_rate) + "," + str(self.time) + "," + str(self.nframes)

def make_graph(data, filename):
    pyplot.clf()
    # pyplot.plot(data)
    # pyplot.savefig(filename)


s = SoundPlay()

s.get_wav_data("canon.wav")
data = fft.rfft(s.data)
data = abs(data)
pyplot.plot(data[:400])
pyplot.savefig('fft0.png')
pyplot.clf()

s = SoundPlay()
s.get_wav_data("fast_canon.wav")
data = fft.rfft(s.data)
data = abs(data)
pyplot.plot(data[:400])
pyplot.savefig('fft1.png')
pyplot.clf()

s = SoundPlay()
s.get_wav_data("slow_canon.wav")
data = fft.rfft(s.data)
data = abs(data)
pyplot.plot(data[:400])
pyplot.savefig('fft2.png')