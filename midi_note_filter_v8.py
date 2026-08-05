"""
midi_note_filter_v8.py
BasicPitch MIDI melody cleaner (V8)
"""
import sys
from music21 import converter, stream, note, chord, tempo

LOW_NOTE=50
HIGH_NOTE=90
MIN_DURATION=0.20
STEP=0.10
MAX_JUMP=18

def q(v): return round(v*4)/4

def filter_midi(src,dst):
    score=converter.parse(src)
    candidates=[]
    for e in score.flatten().notes:
        if isinstance(e,chord.Chord):
            p=max(e.pitches,key=lambda x:x.midi)
            if LOW_NOTE<=p.midi<=HIGH_NOTE:
                n=note.Note(p)
                n.offset=e.offset
                n.duration=e.duration
                candidates.append(n)
        elif isinstance(e,note.Note):
            if LOW_NOTE<=e.pitch.midi<=HIGH_NOTE and e.duration.quarterLength>=MIN_DURATION:
                candidates.append(e)

    timeline={}
    for n in candidates:
        k=round(n.offset/STEP)*STEP
        timeline.setdefault(k,[]).append(n)

    melody=[]
    last=None
    for t in sorted(timeline):
        group=timeline[t]
        if last is None:
            best=max(group,key=lambda x:x.pitch.midi)
        else:
            valid=[x for x in group if abs(x.pitch.midi-last)<=MAX_JUMP]
            if not valid:
                valid=group
            best=min(valid,key=lambda x:abs(x.pitch.midi-last))
        melody.append(best)
        last=best.pitch.midi

    out=stream.Stream()
    part=stream.Part()
    part.insert(0,tempo.MetronomeMark(number=80))
    for n in melody:
        nn=note.Note(n.pitch)
        nn.offset=q(n.offset)
        nn.duration.quarterLength=max(0.25,q(n.duration.quarterLength))
        part.insert(nn.offset,nn)
    out.insert(0,part)
    out.write("midi",fp=dst)
    print("Input notes:",len(candidates))
    print("Output melody:",len(melody))
    print("Saved:",dst)

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: python midi_note_filter_v8.py input.mid output.mid")
        sys.exit(1)
    filter_midi(sys.argv[1],sys.argv[2])
