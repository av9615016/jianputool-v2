import sys
import math

from music21 import (
    converter,
    stream,
    note,
    chord,
    meter,
    tempo,
    tie
)


# =====================================
# JianpuTool MIDI → MusicXML V35
# Melody Stable Version
# =====================================


# =====================================
# MIDI 讀取
# =====================================

def extract_notes(mid):

    print("讀取 MIDI...")


    score = converter.parse(mid)


    notes = []


    for n in score.recurse():


        # 單音

        if isinstance(n, note.Note):


            notes.append(
                (
                    n.pitch.midi,
                    float(n.offset),
                    float(n.duration.quarterLength)
                )
            )


        # 和弦取最高音

        elif isinstance(n, chord.Chord):


            pitch = max(
                n.pitches
            ).midi


            notes.append(
                (
                    pitch,
                    float(n.offset),
                    float(n.duration.quarterLength)
                )
            )


    print(
        "原始音符:",
        len(notes)
    )


    return notes




# =====================================
# 人聲音域
# =====================================

def filter_range(notes):


    result = []


    for p,o,d in notes:


        # 女聲/男聲共同範圍

        if 45 <= p <= 95:


            result.append(
                (
                    p,
                    o,
                    d
                )
            )


    print(
        "音域保留:",
        len(result)
    )


    return result




# =====================================
# 節奏量化
# =====================================

def quantize(value):


    # 1/4 beat 格

    return round(
        value * 4
    ) / 4




# =====================================
# 去除重複
# =====================================

def remove_duplicate(notes):


    result=[]


    last=None


    for item in sorted(
        notes,
        key=lambda x:x[1]
    ):


        key=(

            item[0],

            round(
                item[1],
                2
            )

        )


        if key != last:


            result.append(
                item
            )


            last=key



    print(
        "去除重複:",
        len(result)
    )


    return result




# =====================================
# Phrase Merge + Rhythm Fix
# =====================================

def phrase_merge(notes):


    result=[]


    for p,o,d in notes:


        # 修正時間

        o = quantize(o)

        d = quantize(d)



        # 最短16分音符

        if d < 0.25:

            d = 0.25



        # 最大不要超過4拍

        if d > 4:

            d = 4



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
# 安全4/4小節重建
# 避免 jianpu-ly barcheck fail
# =====================================

def rebuild_measures(score):

    print(
        "重新建立4/4小節..."
    )


    new_score = stream.Score()


    for part in score.parts:


        new_part = stream.Part()


        measure = stream.Measure(
            number=1
        )


        current = 0



        for el in part.flatten().notesAndRests:


            length = float(
                el.duration.quarterLength
            )


            # 節奏安全化

            length = quantize(
                length
            )


            if length <= 0:

                continue



            # 超過小節直接切斷

            if length > 4:

                length = 4

                el.duration.quarterLength = length



            # 跨小節處理

            if current + length > 4:


                remain = 4-current


                if remain > 0:


                    measure.append(
                        note.Rest(
                            quarterLength=remain
                        )
                    )


                new_part.append(
                    measure
                )


                measure = stream.Measure(
                    number=
                    measure.number + 1
                )


                current = 0



            # 移除 tie

            if hasattr(el, "tie"):

                el.tie = None



            el.duration.quarterLength = length


            measure.append(
                el
            )


            current += length




        # 最後補滿4拍

        if current < 4:


            remain = quantize(
                4-current
            )


            if remain >= 0.25:


                measure.append(
                    note.Rest(
                        quarterLength=remain
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

def create_musicxml(
        notes,
        output
):


    print(
        "建立 MusicXML..."
    )


    score = stream.Score()


    part = stream.Part()



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



    for p,o,d in notes:


        n = note.Note(
            p
        )


        n.duration.quarterLength = quantize(
            d
        )


        part.insert(
            o,
            n
        )



    score.append(
        part
    )



    score = score.makeMeasures()



    score = rebuild_measures(
        score
    )



    score.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )





# =====================================
# Main
# =====================================

def main():


    if len(sys.argv) < 3:


        print(
            "使用方式:"
        )


        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )


        return



    midi_file = sys.argv[1]


    output_file = sys.argv[2]



    notes = extract_notes(
        midi_file
    )


    notes = filter_range(
        notes
    )


    notes = remove_duplicate(
        notes
    )


    notes = phrase_merge(
        notes
    )



    create_musicxml(
        notes,
        output_file
    )





if __name__ == "__main__":

    main()