import sys
import os
from music21 import converter, stream, note, chord, meter, tempo


# ===============================
# Melody Extractor V33
# ===============================


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

        elif isinstance(n, chord.Chord):

            # 取最高音當旋律
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



# ===============================
# 音域過濾
# ===============================


def filter_range(notes):

    result=[]

    for p,o,d in notes:

        # 人聲主要範圍
        if 45 <= p <= 90:

            result.append(
                (p,o,d)
            )


    print("音域保留:",len(result))

    return result



# ===============================
# 去除時間重複
# ===============================


def remove_duplicate(notes):

    result=[]

    last=None


    for item in sorted(notes,key=lambda x:x[1]):

        key=(item[0],round(item[1],2))


        if key != last:

            result.append(item)

            last=key


    print("去除重複:",len(result))

    return result



# ===============================
# Phrase Merge
# ===============================


def phrase_merge(notes):

    if not notes:
        return notes


    result=[]


    for n in notes:

        p,o,d=n


        # 太短音合併
        if d < 0.25:

            d=0.25


        result.append(
            (p,o,d)
        )


    print("Phrase Merge:",len(result))

    return result




# ===============================
# 修正小節長度
# 解決 jianpu-ly KeyError 9.5
# ===============================


def fix_measure(score):

    print("Measure Quantize...")


    for m in score.parts[0].getElementsByClass("Measure"):


        dur=m.duration.quarterLength


        if dur < 4:


            rest_time=4-dur


            if rest_time>0:


                m.append(
                    note.Rest(
                        quarterLength=rest_time
                    )
                )


        elif dur > 4:


            print(
                "修正小節:",
                m.number,
                dur
            )


    return score



# ===============================
# 建立 MusicXML
# ===============================


def create_musicxml(notes,out):


    print("建立 MusicXML...")


    s=stream.Score()


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


    s.append(part)



    # 分小節
    s=s.makeMeasures()


    s=fix_measure(s)



    s.write(
        "musicxml",
        fp=out
    )


    print("完成:",out)




# ===============================
# Main
# ===============================


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


    notes=extract_notes(midi)


    notes=filter_range(notes)


    notes=remove_duplicate(notes)


    notes=phrase_merge(notes)


    create_musicxml(
        notes,
        output
    )



if __name__=="__main__":

    main()