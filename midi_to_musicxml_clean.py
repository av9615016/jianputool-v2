# ============================================================
# midi_to_musicxml_clean.py
#
# JianpuTool Professional MVP 3.1
#
# Vocal MIDI -> MusicXML
#
# ============================================================

import sys
import music21



# ============================================================
# 讀取 MIDI
# ============================================================

def load_midi(path):

    print("讀取 MIDI...")

    return music21.converter.parse(path)



# ============================================================
# MIDI 旋律抽取
#
# Note 保留
# Chord 取最高音
# ============================================================

def extract_notes(score):

    print("分析旋律...")


    notes=[]


    for part in score.parts:


        for n in part.recurse().notes:


            if isinstance(
                n,
                music21.note.Note
            ):

                notes.append(n)



            elif isinstance(
                n,
                music21.chord.Chord
            ):


                p=max(
                    n.pitches,
                    key=lambda x:x.midi
                )


                nn=music21.note.Note(
                    p
                )


                nn.offset=n.offset

                nn.duration=n.duration


                notes.append(
                    nn
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
# Vocal Filter
# 保留流行歌
# ============================================================

def melody_filter(notes):


    print(
        "Vocal Melody Filter..."
    )


    result=[]


    last_time=-999



    for n in notes:


        pitch=n.pitch.midi


        length=n.duration.quarterLength



        # 人聲範圍

        if pitch < 25:

            continue


        if pitch > 110:

            continue



        # 太短雜訊

        if length < 0.02:

            continue



        # 完全同時間重複

        if abs(
            n.offset-last_time
        ) < 0.005:

            continue



        result.append(
            n
        )


        last_time=n.offset



    print(
        "保留旋律:",
        len(result)
    )


    return result



# ============================================================
# 建立 4/4 MusicXML
# ============================================================

def build_score(notes):


    print(
        "建立 MusicXML..."
    )


    score=music21.stream.Score()


    part=music21.stream.Part()



    part.append(
        music21.meter.TimeSignature(
            "4/4"
        )
    )


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



        length=float(
            n.duration.quarterLength
        )


        if length<=0:

            length=0.25



        if length>4:

            length=4



        new_note=music21.note.Note(
            n.pitch
        )


        new_note.duration.quarterLength=length



        # ----------------------------
        # 4拍切小節
        # ----------------------------

        if beat + length > 4.0:


            remaining=4.0-beat


            # 剩餘空間

            if remaining>0:


                tie_note=music21.note.Note(
                    n.pitch
                )


                tie_note.duration.quarterLength=remaining


                tie_note.tie=music21.tie.Tie(
                    "start"
                )


                measure.append(
                    tie_note
                )



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



            remain=length-remaining


            if remain>0:


                new_note.duration.quarterLength=remain


                new_note.tie=music21.tie.Tie(
                    "stop"
                )



        measure.append(
            new_note
        )


        beat += length



        # 保險

        if beat>=4.0:


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



    if len(measure.notes)>0:

        part.append(
            measure
        )



    score.append(
        part
    )


    # 再次整理小節

    score.makeMeasures(
        inPlace=True
    )


    return score



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv)<3:

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]



    midi=load_midi(
        inp
    )


    notes=extract_notes(
        midi
    )


    notes=melody_filter(
        notes
    )


    score=build_score(
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