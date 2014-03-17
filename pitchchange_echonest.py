#!/usr/bin/env python
# encoding: utf-8
import os
import sys

from echonest.remix import audio, modify

def main(input_filename, output_filename):
    soundtouch = modify.Modify()
    audiofile = audio.LocalAudioFile(input_filename)
    beats = audiofile.analysis.beats
    out_shape = (len(audiofile.data),)
    out_data = audio.AudioData(shape=out_shape, numChannels=1, sampleRate=44100)
    
    for i, beat in enumerate(beats):
        data = audiofile[beat].data
        number = beat.local_context()[0] % 12
        new_beat = soundtouch.shiftPitchSemiTones(audiofile[beat], number*-1)
        out_data.append(new_beat)
    
    out_data.encode(output_filename)

if __name__ == '__main__':
    main('music/m1.mp3', 'music/m1_high.mp3')
