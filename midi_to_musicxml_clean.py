# ============================================================
# midi_to_musicxml_clean_v41_pro.py
#
# JianpuTool Professional
#
# Vocal MIDI -> MusicXML
#
# Fix:
#   Duration Type Error
#   Measure Overflow
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


                nn.duration = n.duration

                nn.offset = n.offset


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
# Vocal Preserve
# ============================================================

def vocal_filter(notes):


    print(
        "Vocal Melody Preserve..."
    )


    result=[]


    last=None



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



        # 移除極短雜訊

        if length < 0.05:
            continue



        # 同音完全重疊

        if last:

            if (
                pitch==last.pitch.midi
                and
                abs(
                    n.offset-last.offset
                ) < 0.01
            ):
                continue



        result.append(n)

        last=n



    print(
        "保留旋律:",
        len(result)
    )


    return result



# ============================================================
# Safe Duration
# ============================================================

def safe_duration(note, length):


    if length <= 0:

        length=0.25



    d=music21.duration.Duration(
        length
    )


    # 強制建立 MusicXML type

    d.linked=True


    note.duration=d



# ============================================================
# Build 4/4
# ============================================================

def build_score(notes):


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


    beat=0.0



    for n in notes:


        pitch=n.pitch


        length=float(
            n.duration.quarterLength
        )


        if length<=0:

            length=0.25



        if length>4:

            length=4



        remain=length



        while remain>0:



            space=4.0-beat


            take=min(
                remain,
                space
            )



            new_note=music21.note.Note(
                pitch
            )



            safe_duration(
                new_note,
                take
            )



            # 跨小節

            if take < remain:

                new_note.tie=music21.tie.Tie(
                    "start"
                )


            elif remain < length:

                new_note.tie=music21.tie.Tie(
                    "stop"
                )



            measure.append(
                new_note
            )


            beat += take

            remain -= take



            if beat >= 4.0-0.001:


                measure.rightBarline=(
                    music21.bar.Barline(
                        "regular"
                    )
                )


                part.append(
                    measure
                )


                measure_no += 1


                measure=music21.stream.Measure(
                    number=measure_no
                )


                beat=0.0



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
        "整理 MusicXML..."
    )


    # 修正 duration type

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
            "python midi_to_musicxml_clean_v41_pro.py input.mid output.musicxml"
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


    notes=vocal_filter(
        notes
    )


    score=build_score(
        notes
    )


    save(
        score,
        out
    )



if __name__=="__main__":

    main()