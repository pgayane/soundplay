"""Reverse a song by playing its beats forward starting from the end of the song"""
import echonest.remix.audio as audio

# Easy around wrapper mp3 decoding and Echo Nest analysis
audio_file = audio.LocalAudioFile("music/Future Islands - Tin Man.mp3")

print audio_file.duration
# You can manipulate the beats in a song as a native python list
beats = audio_file.analysis.beats
print 'number of bars', len(audio_file.analysis.bars)
print 'number of beats', len(audio_file.analysis.beats)
print 'number of tatums', len(audio_file.analysis.tatums)
print 'number of sections', len(audio_file.analysis.sections)
print 'number of segments', len(audio_file.analysis.segments)
beats.reverse()

# And render the list as a new audio file!
audio.getpieces(audio_file, beats).encode("reversed.wav")