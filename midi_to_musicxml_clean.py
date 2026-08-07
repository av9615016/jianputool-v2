import sys
from music21 import converter, stream, note, meter, tempo


# =====================================
# JianpuTool MIDI → MusicXML V34
# =====================================


# -------------------------------
# 讀取 MIDI
# -------------------------------

def extract_notes(mid):

    print("讀取 MIDI...")

    score = converter.parse(mid)

    notes = []

    for n in score.recurse():

        if isinstance(n, note.Note):

            notes.append(
                (
                    n.pitch.midi,
                    n.offset,
                    n.duration.quarterLength
                )
            )

        elif n.isChord:

            p = max(n.pitches).midi

            notes.append(
                (
                    p,
                    n.offset,
                    n.duration.quarterLength
                )
            )


    print("原始音符:", len(notes))

    return notes



# -------------------------------
# 人聲音域
# -------------------------------

def filter_range(notes):

    result=[]

    for p,o,d in notes:

        # 人聲常用範圍

        if 45 <= p <= 90:

            result.append(
                (p,o,d)
            )


    print("音域保留:",len(result))

    return result




# -------------------------------
# 去除重複音符
# -------------------------------

def remove_duplicate(notes):

    result=[]

    last=None


    for item in sorted(
        notes,
        key=lambda x:x[1]
    ):

        key=(
            item[0],
            round(item[1],2)
        )


        if key != last:

            result.append(item)

            last=key


    print(
        "去除重複:",
        len(result)
    )


    return result




# -------------------------------
# Phrase Merge
# -------------------------------

def phrase_merge(notes):

    result=[]


    for p,o,d in notes:


        # 太短音修正

        if d < 0.25:

            d=0.25


        result.append(
            (
                p,
                o,
                d
            )
        )


    print(
        "Phrase Merge:",
        len(result)
    )


    return result




# =====================================
# 重新建立 4/4 小節
# 修復 jianpu-ly KeyError
# =====================================


def rebuild_measures(score):

    print(
        "重新建立4/4小節..."
    )


    new_score=stream.Score()



    for part in score.parts:


        new_part=stream.Part()


        elements=list(
            part.flatten()
            .notesAndRests
        )


        measure=stream.Measure(
            number=1
        )


        current=0



        for el in elements:


            length=el.duration.quarterLength



            # 超過4拍換小節

            if current + length > 4:


                remain=4-current


                if remain > 0:

                    measure.append(
                        note.Rest(
                            quarterLength=remain
                        )
                    )


                new_part.append(
                    measure
                )


                measure=stream.Measure(
                    number=
                    measure.number+1
                )


                current=0



            measure.append(el)


            current += length




        # 補滿最後小節

        if current < 4:

            measure.append(
                note.Rest(
                    quarterLength=4-current
                )
            )



        new_part.append(
            measure
        )


        new_score.append(
            new_part
        )


    return new_score





# =====================================
# 建立 MusicXML
# =====================================

def create_musicxml(notes,out):


    print(
        "建立 MusicXML..."
    )


    score=stream.Score()


    part=stream.Part()



    part.append(
        meter.TimeSignature("4/4")
    )


    part.append(
        tempo.MetronomeMark(
            number=80
        )
    )



    for p,o,d in notes:


        n=note.Note(p)


        n.duration.quarterLength=d


        part.insert(
            o,
            n
        )



    score.append(part)



    score=score.makeMeasures()



    score=rebuild_measures(
        score
    )



    score.write(
        "musicxml",
        fp=out
    )


    print(
        "完成:",
        out
    )





# =====================================
# 主程式
# =====================================


def main():

    if len(sys.argv)<3:

        print(
            "使用方式:"
        )

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        return



    midi=sys.argv[1]

    output=sys.argv[2]



    notes=extract_notes(
        midi
    )


    notes=filter_range(
        notes
    )


    notes=remove_duplicate(
        notes
    )


    notes=phrase_merge(
        notes
    )


    create_musicxml(
        notes,
        output
    )




if __name__=="__main__":

    main()