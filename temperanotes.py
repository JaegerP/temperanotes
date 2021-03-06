from __future__ import division
from math import log, sqrt
import argparse, sys

note_names_sharp = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
note_names_flat  = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']

def get_key_index(key):
    if len(key) == 1:
        key_index = note_names_sharp.index(key)
    else:
        if key in note_names_sharp:
            key_index = note_names_sharp.index(key)
        else:
            key_index = note_names_flat.index(key)      # let it fail here, if a wrong note name was specified
    return key_index


def frequencies(temperament, notes_low, notes_high, key = 'C', base_freq = 440.0, key_freq = 'A'):
    key_index     = get_key_index(key)
    keyfreq_index = get_key_index(key_freq)
    use_base_freq = base_freq / temperament[keyfreq_index - key_index]
    freq = []
    for fullnote in range(-notes_low, notes_high):
        octave, note = divmod(fullnote, 12)
        freq.append((use_base_freq * 2 ** octave) * temperament[note])
    return freq

def equal_temperament():
    return [ 2. ** (i/12)  for i in range(12)]

def to_cents(temperament):
    a = temperament[0]
    return [int(1200 * log(t / a, 2) + .5) for t in temperament]

def myeval(x, integer=False):
    e = None
    r = None
    try:
        if integer:
            r = int(eval(x) + .5)
        else:
            r = eval(x)
    except Exception as ex:
        e = ex
    return r, e

def verify(temp, cents):
    computed_cents = to_cents(temp)
    for i, c in enumerate(computed_cents):
        if c != cents[i]:
            print >> sys.stderr, "Warning: cent different for", str(i) + "th element", c, "vs", cents[i]

def read_temperament(t):
    temp = []
    cents = []
    exceptions = []
    must_exit = False
    for line in t.splitlines(True):
        useful = line.split("#")[0].strip()
        if useful:
            stuff = useful.split(",")
            result, excp = myeval(stuff[0])
            temp.append(result)
            exceptions.append(excp)
            if len(stuff) == 2:
                result, excp = myeval(stuff[1], integer=True)
                cents.append(result)
                exceptions.append(excp)
            elif len(stuff) > 2:
                print >> sys.stderr, "Temperament file can not have more than 2 entries per line"
                print >> sys.stderr, "     instead it has in line:"
                print >> sys.stderr, line
                must_exit = True

    if len(temp) != 12:
        print >> sys.stderr, "Temperament file must have 12 entries for the chromatic scale"
        print >> sys.stderr, "     instead it has", len(temp)
        must_exit = True

    if len(cents) != 12 and len(cents) != 0:
        print >> sys.stderr, "Temperament file must have 0 or 12 entries for the chromatic scale"
        print >> sys.stderr, "     for the cents field. Instead it has", len(cents)
        must_exit = True

    real_exceptions = [value for value in exceptions if value is not None]
    if len(real_exceptions) > 0:
        print >> sys.stderr, "Problems reading temperament file"
        print >> sys.stderr, real_exceptions
        must_exit = True
    if must_exit:
        sys.exit(1)
    return temp, cents

def piano(temp):
    piano = frequencies(temp, notes_low = 3*12 + 3, notes_high = 4*12 + 1)  # starts from middle C
    return piano

def midi(temp, key='C', key_freq='A', freq=440.):
    # midi specs say that note #60 is middle C, i.e. there are 60 notes lower than that
    midi = frequencies(temp, notes_low = 5*12, notes_high = 5*12 + 8,
                       key=key, key_freq=key_freq, base_freq=freq)
    return midi

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("temperament", type=argparse.FileType('r'), nargs='?',
                                      help="Temperament file, see README.md for details")
    group.add_argument("-e", "--equal", action="store_true", default = False,
                                       help="Ignore TEMPERAMENT, use ET-12 instead")
    parser.add_argument("-t", "--timidity", action="store_true", default = False,
                                       help="Output in timidity format")

    args = parser.parse_args()
    if args.equal:
        temp = equal_temperament()
    else:
        temp, cents = read_temperament(args.temperament.read())
        verify(temp, cents)

    if args.timidity:
        for freq in midi(temp):
            print int(freq * 1000)
    else:
        print midi(temp)
