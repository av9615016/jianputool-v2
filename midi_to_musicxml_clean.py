# ==========================================================
# midi_to_musicxml_clean_v42_3_pro.py
#
# JianpuTool Professional
#
# MIDI Vocal Melody
# -> Clean Melody
# -> MusicXML
#
# V42.3 PRO
#
# ==========================================================


import sys
import os
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import tempo
from music21 import key


# ==========================================================
# CONFIG
# ==========================================================

MIN_PITCH = 45
MAX_PITCH = 90

MIN_DURATION = 0.15

MERGE_GAP = 0.08


# ==========================================================
# LOAD MIDI
# ==========================================================

def load_midi(path):

    print("讀取 MIDI...")

    midi = converter.parse(path)

    return midi



# ==========================================================
# EXTRACT NOTES
# ==========================================================

def extract_notes(midi):

    print("抽取旋律...")


    notes=[]


    for n in midi.flatten().notes:

        if not isinstance(n, note.Note):
            continue


        pitch=n.pitch.midi


        dur=n.duration.quarterLength


        notes.append({

            "pitch":pitch,
            "offset":n.offset,
            "duration":dur

        })


    print("原始音符:",len(notes))

    return notes



# ==========================================================
# RANGE FILTER
# ==========================================================

def filter_range(notes):

    result=[]


    for n in notes:

        if MIN_PITCH <= n["pitch"] <= MAX_PITCH:

            if n["duration"] >= MIN_DURATION:

                result.append(n)


    print(
        "音域/長度保留:",
        len(result)
    )


    return result



# ==========================================================
# REMOVE DUPLICATE
# ==========================================================

def remove_duplicate(notes):

    result=[]


    last=None


    for n in notes:


        key=(
            n["pitch"],
            round(n["offset"],3)
        )


        if key!=last:

            result.append(n)

            last=key


    print(
        "去除重複:",
        len(result)
    )


    return result



# ==========================================================
# MERGE PHRASE
# ==========================================================

def merge_phrase(notes):


    if not notes:
        return []


    result=[]


    current=copy.deepcopy(notes[0])


    for n in notes[1:]:


        end=current["offset"]+current["duration"]


        gap=n["offset"]-end


        if (
            n["pitch"]==current["pitch"]
            and gap <= MERGE_GAP
        ):

            current["duration"] += (
                gap+n["duration"]
            )


        else:

            result.append(current)

            current=copy.deepcopy(n)



    result.append(current)



    print(
        "Phrase Merge:",
        len(result)
    )


    return result




# ==========================================================
# CREATE MUSICXML
# ==========================================================

def create_musicxml(notes,outfile):


    print("建立 MusicXML...")


    score=stream.Score()


    part=stream.Part()


    part.insert(
        0,
        tempo.MetronomeMark(
            number=80
        )
    )


    part.insert(
        0,
        key.Key("C")
    )


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    for n in notes:


        nn=note.Note(
            n["pitch"]
        )


        nn.duration.quarterLength = (
            min(
                n["duration"],
                4
            )
        )


        part.append(nn)



    score.append(part)



    # safety

    for p in score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            if m.duration.quarterLength == 0:

                m.insert(
                    0,
                    note.Rest(
                        quarterLength=4
                    )
                )


    score.write(
        "musicxml",
        fp=outfile
    )


    print(
        "完成:",
        outfile
    )



# ==========================================================
# MAIN
# ==========================================================

def main():


    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python midi_to_musicxml_clean_v42_3_pro.py input.mid output.musicxml"
        )

        sys.exit(1)



    infile=sys.argv[1]

    outfile=sys.argv[2]



    midi=load_midi(infile)


    notes=extract_notes(midi)


    notes=filter_range(notes)


    notes=remove_duplicate(notes)


    notes=merge_phrase(notes)



    create_musicxml(
        notes,
        outfile
    )



if __name__=="__main__":

    main()