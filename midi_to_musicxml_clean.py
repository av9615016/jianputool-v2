# ============================================================
# midi_to_musicxml_clean_v40_pro.py
#
# JianpuTool Professional MVP 3.0
#
# Vocal MIDI -> MusicXML
#
# 流行歌曲旋律模式
#
# ============================================================

import sys
import music21


# ============================================================
# MIDI 讀取
# ============================================================

def load_midi(path):

    print("讀取 MIDI...")

    midi = music21.converter.parse(path)

    return midi



# ============================================================
# 找旋律
# ============================================================

def extract_melody(score):


    print("分析旋律...")


    parts = score.parts


    if len(parts) == 0:

        return score



    # 取最高音平均線
    notes = []


    for p in parts:


        for n in p.recurse().notes:


            notes.append(n)



    print(
        "候選音符:",
        len(notes)
    )



    # 依時間排序

    notes.sort(
        key=lambda x:x.offset
    )


    return notes



# ============================================================
# Vocal Melody Filter
# ============================================================

def melody_filter(notes):


    print(
        "Vocal Melody Filter..."
    )


    result=[]


    last_time=-1



    for n in notes:


        pitch=n.pitch.midi


        duration=n.duration.quarterLength



        # 人聲範圍

        if pitch < 35:
            continue


        if pitch > 100:
            continue



        # 去除極短雜訊

        if duration < 0.08:
            continue



        # 避免完全重疊

        if abs(
            n.offset-last_time
        ) < 0.03:

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
# 建立 MusicXML
# ============================================================

def create_score(notes):


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


    # tempo

    part.append(
        music21.tempo.MetronomeMark(
            number=80
        )
    )



    current_measure=music21.stream.Measure(
        number=1
    )


    beat=0



    for n in notes:


        new_note=music21.note.Note(
            n.pitch
        )


        length=n.duration.quarterLength


        # 避免超長

        if length > 4:

            length=4



        new_note.duration.quarterLength=length



        # 小節控制

        if beat + length > 4:


            current_measure.rightBarline = (
                music21.bar.Barline(
                    "regular"
                )
            )


            part.append(
                current_measure
            )


            current_measure=music21.stream.Measure(
                number=current_measure.number+1
            )


            beat=0



        current_measure.append(
            new_note
        )


        beat += length



    if len(current_measure.notes)>0:

        part.append(
            current_measure
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
            "python midi_to_musicxml_clean_v40_pro.py input.mid output.musicxml"
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


    score=create_score(
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