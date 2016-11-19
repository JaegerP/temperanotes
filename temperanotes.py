from __future__ import division

def frequencies(temperament, octaves_low, octaves_high, base_freq = 440.0):
    freq = []
    for octave in range(1, octaves_low + 1):
        freq =  [(base_freq / 2 ** octave) * note for note in temperament] + freq
    for octave in range(octaves_high):
        freq += [(base_freq * 2 ** octave) * note for note in temperament]
    return freq

def equal_temperament():
    return [ 2. ** (i/12)  for i in range(12)]
