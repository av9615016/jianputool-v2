# ============================================================
# midi_to_musicxml_clean_v43_pro.py
#
# JianpuTool Professional
#
# Vocal MIDI -> MusicXML
#
# Fix:
#   measure > 4 beats
#   jianpu_ly KeyError 8.75/9.25/9.5
#
# ============================================================


import sys

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo
from music21 import duration



# ============================================================
# Duration
# ============================================================

def safe_duration(ql):

    if ql <= 0:
        ql = 0.25


    d = duration.Duration(
        ql
    )


    if d.type is None:

        if ql >= 4:
            d.type="whole"

        elif ql >= 2:
            d.type="half"

        elif ql >= 1:
            d.type="quarter"

        elif ql >= 0.5:
            d.type="eighth"

        else:
            d.type="16th"


    return d



# ============================================================
# Extract MIDI
# ============================================================

def extract_notes(path):


    print("讀取 MIDI...")


    midi = converter.parse(
        path
    )


    notes=[]


    for p in midi.parts:


        for n in p.recurse().notes:


            if isinstance(n,note.Note):

                notes.append(n)



            elif isinstance(n,chord.Chord):


                top=max(
                    n.pitches,
                    key=lambda x:x.midi
                )


                nn=note.Note(
                    top
                )


                nn.offset=n.offset

                nn.duration=n.duration


                notes.append(nn)



    notes.sort(
        key=lambda x:x.offset
    )


    print(
        "候選音符:",
        len(notes)
    )


    return notes



# ============================================================
# Preserve Vocal
# ============================================================

def melody_filter(notes):


    print(
        "Vocal Melody Preserve..."
    )


    result=[]


    last=-1



    for n in notes:


        p=n.pitch.midi


        q=float(
            n.duration.quarterLength
        )


        if p < 30:
            continue


        if p > 108:
            continue


        if q < 0.05:
            continue



        if p==last:

            continue


        result.append(n)


        last=p



    print(
        "保留旋律:",
        len(result)
    )


    return result



# ============================================================
# Create strict 4/4
# ============================================================

def build_score(notes):


    print(
        "建立嚴格4/4 MusicXML..."
    )


    score=stream.Score()


    part=stream.Part()


    part.append(
        meter.TimeSignature(
            "4/4"
        )
    )


    part.append(
        tempo.MetronomeMark(
            number=80
        )
    )



    measure=stream.Measure(
        number=1
    )


    beat=0



    for src in notes:


        remain=float(
            src.duration.quarterLength
        )


        while remain > 0:


            available=4-beat


            use=min(
                remain,
                available
            )



            n=note.Note(
                src.pitch
            )


            n.duration=safe_duration(
                use
            )


            measure.append(
                n
            )


            beat += use

            remain -= use



            # 滿4拍立即換小節

            if beat >= 3.999:


                part.append(
                    measure
                )


                measure=stream.Measure(
                    number=
                    measure.number+1
                )


                beat=0



    if len(
        measure.notes
    )>0:


        part.append(
            measure
        )



    score.append(
        part
    )


    return score



# ============================================================
# Save
# ============================================================

def save(score,out):


    print(
        "輸出 MusicXML..."
    )


    score.write(
        "musicxml",
        fp=out
    )


    print(
        "完成:",
        out
    )



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv)<3:

        print(
            "python midi_to_musicxml_clean_v43_pro.py input.mid output.musicxml"
        )

        return



    midi=sys.argv[1]

    xml=sys.argv[2]



    notes=extract_notes(
        midi
    )


    notes=melody_filter(
        notes
    )


    score=build_score(
        notes
    )


    save(
        score,
        xml
    )



if __name__=="__main__":

    main()