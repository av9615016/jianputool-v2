from music21 import stream, note, meter, tempo
from mido import MidiFile
import sys


if len(sys.argv) < 3:
    print("usage: python midi_to_musicxml_simple_v3.py input.mid output.musicxml")
    exit()


src=sys.argv[1]
dst=sys.argv[2]


print("LOAD MIDI:",src)


mid=MidiFile(src)


score=stream.Score()

part=stream.Part()


part.append(
    meter.TimeSignature("4/4")
)

part.append(
    tempo.MetronomeMark(number=120)
)


notes=[]


# =====================
# 讀取 MIDI note_on
# =====================

for track in mid.tracks:

    for msg in track:

        if msg.type=="note_on" and msg.velocity>0:

            notes.append(msg.note)



print("NOTES:",len(notes))



# =====================
# 建立 Music21
# 每個音一拍
# =====================

for pitch in notes:

    n=note.Note(pitch)

    n.duration.quarterLength=1

    part.append(n)



score.append(part)



score.write(
    "musicxml",
    fp=dst
)


print("DONE:",dst)