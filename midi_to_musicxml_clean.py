# ============================================================
# midi_to_musicxml_clean_v42_pro.py
#
# JianpuTool Professional
#
# Vocal MIDI -> MusicXML
#
# Fix V42:
# Duration type error
#
# ============================================================

import sys

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import duration
from music21 import meter
from music21 import tempo
from music21 import bar



# ============================================================
# Duration Fix
# ============================================================

def fix_duration(n, ql):

    if ql <= 0:
        ql = 0.25


    d = duration.Duration(
        ql
    )


    # 強制讓 music21 產生 type

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



    n.duration = d



# ============================================================
# Load
# ============================================================

def load_midi(path):

    print("讀取 MIDI...")

    return converter.parse(path)



# ============================================================
# Extract
# ============================================================

def extract_notes(score):

    print("分析旋律...")


    result=[]


    for p in score.parts:


        for x in p.recurse().notes:


            if isinstance(
                x,
                note.Note
            ):

                result.append(x)



            elif isinstance(
                x,
                chord.Chord
            ):

                # 和弦取最高音

                top=max(
                    x.pitches,
                    key=lambda p:p.midi
                )


                n=note.Note(
                    top
                )


                n.offset=x.offset

                n.duration=x.duration


                result.append(n)



    result.sort(
        key=lambda n:n.offset
    )


    print(
        "候選音符:",
        len(result)
    )


    return result



# ============================================================
# Melody Preserve
# ============================================================

def melody_filter(notes):


    print(
        "Vocal Melody Preserve..."
    )


    out=[]


    last_offset=-1
    last_pitch=-1



    for n in notes:


        p=n.pitch.midi

        ql=float(
            n.duration.quarterLength
        )



        # 人聲範圍

        if p < 30:
            continue


        if p > 108:
            continue



        # 移除極短雜訊

        if ql < 0.05:
            continue



        # 完全重複

        if (
            p==last_pitch
            and
            abs(n.offset-last_offset)<0.001
        ):

            continue



        out.append(n)


        last_pitch=p
        last_offset=n.offset



    print(
        "保留旋律:",
        len(out)
    )


    return out



# ============================================================
# Build Score
# ============================================================

def create_score(notes):


    print(
        "建立 4/4 MusicXML..."
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



    measure_no=1


    m=stream.Measure(
        number=measure_no
    )


    beat=0



    for src in notes:


        remain=float(
            src.duration.quarterLength
        )


        if remain<=0:

            remain=0.25



        if remain>4:

            remain=4



        while remain>0:


            space=4-beat


            use=min(
                remain,
                space
            )



            n=note.Note(
                src.pitch
            )


            fix_duration(
                n,
                use
            )



            m.append(
                n
            )



            beat += use

            remain -= use



            if beat >= 4-0.001:


                m.rightBarline=bar.Barline(
                    "regular"
                )


                part.append(
                    m
                )


                measure_no +=1


                m=stream.Measure(
                    number=measure_no
                )


                beat=0



    if len(m.notes)>0:

        part.append(
            m
        )


    score.append(
        part
    )


    return score



# ============================================================
# Extra Safety
# ============================================================

def force_all_duration(score):


    for n in score.recurse().notes:


        q=float(
            n.duration.quarterLength
        )


        fix_duration(
            n,
            q
        )



# ============================================================
# Save
# ============================================================

def save(score,out):


    print(
        "修正 Duration..."
    )


    force_all_duration(
        score
    )


    score.makeNotation(
        inPlace=True
    )


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
            "usage: python midi_to_musicxml_clean_v42_pro.py input.mid output.musicxml"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]


    score=load_midi(
        inp
    )


    notes=extract_notes(
        score
    )


    notes=melody_filter(
        notes
    )


    xml=create_score(
        notes
    )


    save(
        xml,
        out
    )



if __name__=="__main__":

    main()