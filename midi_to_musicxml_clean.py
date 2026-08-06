# ============================================================
# midi_to_musicxml_clean.py
#
# JianpuTool Professional MVP 3.0
#
# MIDI -> MusicXML
#
# Vocal Melody Pro
#
# ============================================================

import sys
import music21



# ============================================================
# Load MIDI
# ============================================================

def load_midi(path):

    print("讀取 MIDI...")

    return music21.converter.parse(path)



# ============================================================
# Extract Melody
#
# Note      -> 保留
# Chord     -> 取最高音
#
# ============================================================

def extract_melody(score):

    print("分析旋律...")


    notes=[]


    for part in score.parts:


        for n in part.recurse().notes:


            # ----------------------------
            # 單音
            # ----------------------------

            if isinstance(
                n,
                music21.note.Note
            ):


                notes.append(
                    n
                )



            # ----------------------------
            # 和弦
            # 取最高音
            # ----------------------------

            elif isinstance(
                n,
                music21.chord.Chord
            ):


                highest=max(
                    n.pitches,
                    key=lambda x:x.midi
                )


                new_note=music21.note.Note(
                    highest
                )


                new_note.offset=n.offset

                new_note.duration=n.duration


                notes.append(
                    new_note
                )



    notes.sort(
        key=lambda x:x.offset
    )


    print(
        "候選音符:",
        len(notes)
    )


    return notes



# ============================================================
# Melody Filter Pro
#
# 保留流行歌旋律
# ============================================================

def melody_filter(notes):


    print(
        "Vocal Melody Filter..."
    )


    result=[]


    last_offset=-1



    for n in notes:


        pitch=n.pitch.midi


        length=n.duration.quarterLength



        # 人聲範圍

        if pitch < 30:
            continue


        if pitch > 100:
            continue



        # 太短雜訊

        if length < 0.05:
            continue



        # 移除完全重疊

        if abs(
            n.offset-last_offset
        ) < 0.02:

            continue



        result.append(
            n
        )


        last_offset=n.offset



    print(
        "保留旋律:",
        len(result)
    )


    return result



# ============================================================
# Build MusicXML
# ============================================================

def create_musicxml(notes):


    print(
        "建立 MusicXML..."
    )


    score=music21.stream.Score()


    part=music21.stream.Part()



    # 4/4

    part.append(
        music21.meter.TimeSignature(
            "4/4"
        )
    )



    # tempo

    part.append(
        music21.tempo.MetronomeMark(
            number=80
        )
    )



    measure=music21.stream.Measure(
        number=1
    )


    beat=0



    for n in notes:


        new_note=music21.note.Note(
            n.pitch
        )


        length=n.duration.quarterLength



        # 限制過長

        if length > 4:

            length=4



        if length <=0:

            length=0.25



        new_note.duration.quarterLength=length



        # 小節控制

        if beat + length > 4:


            measure.rightBarline=(
                music21.bar.Barline(
                    "regular"
                )
            )


            part.append(
                measure
            )


            measure=music21.stream.Measure(
                number=measure.number+1
            )


            beat=0



        measure.append(
            new_note
        )


        beat += length



    if len(measure.notes)>0:

        part.append(
            measure
        )



    score.append(
        part
    )


    return score



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv)<3:


        print(
            "使用:"
        )

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]



    midi=load_midi(
        inp
    )


    notes=extract_melody(
        midi
    )


    notes=melody_filter(
        notes
    )


    score=create_musicxml(
        notes
    )



    score.write(
        "musicxml",
        fp=out
    )


    print(
        "完成:",
        out
    )



if __name__=="__main__":

    main()