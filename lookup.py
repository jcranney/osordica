#Lookup table
# Base 12, C maj at the moment, can expand later
#

factors = {x:2**(x/12) for x in range(-18,19)}

#Cmaj notes
dict_notes = {  "C2":-18,
                "D2":-16,
                "E2":-14,
                "F2":-13,
                "G2":-11,
                "A2":-9,
                "B2":-7,
                "C3":-6,
                "D3":-4,
                "E3":-2,
                "F3":-1,
                "G3":1,
                "A3":3,
                "B3":5,
                "C4":6,
                "D4":8,
                "E4":10,
                "F4":11,
                "G4":13,
                "A4":15,
                "B4":17,
                "C5":18,
                }

lookup_fingerpattern = {
0:      "",
16:     "",
32:     "",
1:      "C3",
2:      "D3",
4:      "E3",
8:      "F3",
64:     "G3",
128:    "A3",
256:    "B3",
512:    "C4",
17:     "C2",
18:     "D2",
20:     "E2",
24:     "F2",
80:     "G2",
144:    "A2",
272:    "B2",
528:    "C3",
33:     "C4",
34:     "D4",
36:     "E4",
40:     "F4",
96:     "G4",
160:    "A4",
288:    "B4",
544:    "C5",
3:      "C3maj",
6:      "D3maj",
12:     "E3maj",
72:     "F3maj",
176:    "G3maj",
384:    "A3maj",
768:    "B3maj",
513:    "C4maj",
19:     "C2maj",
22:     "D2maj",
28:     "E2maj",
88:     "F2maj",
192:    "G2maj",
368:    "A2maj",
784:    "B2maj",
529:    "C3maj",
35:     "C4maj",
38:     "D4maj",
44:     "E4maj",
104:    "F4maj",
208:    "G4maj",
384:    "A4maj",
800:    "B4maj",
545:    "C5maj",
5:      "C3min",
10:     "D3min",
68:     "E3min",
136:    "F3min",
320:    "G3min",
640:    "A3min",
257:    "B3min",
514:    "C4min",
21:     "C2min",
26:     "D2min",
84:     "E2min",
152:    "F2min",
336:    "G2min",
656:    "A2min",
273:    "B2min",
530:    "C3min",
37:	    "C4min",
42:	    "D4min",
100:    "E4min",
168:    "F4min",
352:    "G4min",
672:    "A4min",
289:    "B4min",
546:    "C5min"
}

def left(s, amount):
    if amount<=0:
        return []
    else:
        return s[:amount]

def right(s, amount):
    if amount <=0:
        return []
    else:
        return s[-amount:]

def lookup_sounds(dec_ref):
    try:
        sound = lookup_fingerpattern[dec_ref]
        print(sound)
    except:
        print("Unkown Combination")
        return []
    if sound == "":
        return []
    note = getBase(left(sound,2))
    type = right(sound,len(sound)-2)
    if type == []:
        return [note]
    elif type == "maj":
        return getMaj(note)
    elif type == "min":
        return getMin(note)
    elif type == "aug":
        return getAug(note)
    elif type == "7th":
        return get7th(note)
    

def notes2factor(notes):
    #requires a list of notes
    try:
        return [factors[x] for x in notes]
    except TypeError:
        print("Requires notes to be a list")

def getBase(name):
    return dict_notes[name]
    
def getMaj(idx):
    return [idx, idx+4, idx+7]

def getMin(idx):
    return [idx, idx+3, idx+7]

def getAug(idx):
    return [idx, idx+4, idx+8]

def get7th(idx):
    return [idx, idx+4, idx+7, idx+10]
    
    