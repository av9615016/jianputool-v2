# ============================================================
# midi_to_musicxml_clean_v41_pro.py
#
# JianpuTool Professional
#
# Vocal MIDI -> MusicXML
#
# V41 PRO
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
# Extract melody
# ============================================================

def extract_melody(score):

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

                # chord 取最高音

                p=max(
                    n.pitches,
                    key=lambda x:x.midi
                )


                nn=music21.note.Note(
                    p
                )

                nn.duration=n.duration

                nn.offset=n.offset


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
# Vocal preserve filter
# ============================================================

def vocal_filter(notes):

    print(
        "Vocal Melody Preserve..."
    )


    result=[]


    last_pitch=None
    last_offset=-999



    for n in notes:


        pitch=n.pitch.midi


        length=float(
            n.duration.quarterLength
        )


        # 人聲範圍

        if pitch < 30:
            continue


        if pitch > 108:
            continue



        # 去掉極短雜訊

        if length < 0.05:
            continue



        # 完全同時間同音

        if (
            pitch==last_pitch
            and
            abs(
                n.offset-last_offset
            )<0.01
        ):
            continue



        result.append(n)


        last_pitch=pitch

        last_offset=n.offset



    print(
        "保留旋律:",
        len(result)
    )


    return result



# ============================================================
# Build 4/4 score
# ============================================================

def build_musicxml(notes):


    print(
        "建立 4/4 MusicXML..."
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



    measure_no=1


    measure=music21.stream.Measure(
        number=measure_no
    )


    beat_used=0.0



    for n in notes:



        pitch=n.pitch


        duration=float(
            n.duration.quarterLength
        )



        if duration<=0:

            duration=0.25



        # 避免超長音

        if duration>4:

            duration=4



        remain=duration



        while remain>0:



            space=4.0-beat_used



            take=min(
                remain,
                space
            )


            new_note=music21.note.Note(
                pitch
            )


            new_note.duration.quarterLength=take



            # 跨小節 tie

            if take < remain:


                new_note.tie=music21.tie.Tie(
                    "start"
                )


            elif remain < duration:


                new_note.tie=music21.tie.Tie(
                    "stop"
                )



            measure.append(
                new_note
            )


            beat_used += take

            remain -= take



            # 滿4拍

            if beat_used >= 4.0-0.001:


                measure.rightBarline=(
                    music21.bar.Barline(
                        "regular"
                    )
                )


                part.append(
                    measure
                )


                measure_no +=1


                measure=music21.stream.Measure(
                    number=measure_no
                )


                beat_used=0



    # 最後小節

    if len(measure.notes)>0:

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
        "整理小節..."
    )


    # 強制 4/4

    score.makeMeasures(
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
            "python midi_to_musicxml_clean_v41_pro.py input.mid output.musicxml"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]



    midi=load_midi(inp)


    notes=extract_melody(
        midi
    )


    notes=vocal_filter(
        notes
    )


    score=build_musicxml(
        notes
    )


    save(
        score,
        out
    )



if __name__=="__main__":

    main()