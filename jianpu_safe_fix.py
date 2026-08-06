# ==========================================================
# JianpuTool Professional MVP 2.1
# jianpu_safe_fix.py
#
# MusicXML -> Safe MusicXML
#
# Fix:
#   - barcheck fail
#   - note crosses barline
#   - invalid measure duration
#
# ==========================================================


import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import duration



# ==========================================================
# 設定
# ==========================================================


TARGET_BEATS = 4.0



# ==========================================================
# duration 修正
# ==========================================================

def quantize_duration(n):

    q = n.duration.quarterLength


    allowed = [

        0.25,
        0.5,
        0.75,
        1.0,
        1.5,
        2.0,
        3.0,
        4.0

    ]


    best=min(
        allowed,
        key=lambda x:abs(x-q)
    )


    n.duration.quarterLength = best



# ==========================================================
# 建立 Rest
# ==========================================================

def make_rest(length):

    r = note.Rest()

    r.duration.quarterLength = length

    return r



# ==========================================================
# 小節安全修正
# ==========================================================

def fix_measure(measure):


    total = 0

    new_elements=[]


    for el in measure.notesAndRests:


        quantize_duration(el)


        q=el.duration.quarterLength



        # 超長音切割

        while q > TARGET_BEATS:


            part=copy.deepcopy(el)

            part.duration.quarterLength=TARGET_BEATS

            new_elements.append(part)

            q -= TARGET_BEATS



        el.duration.quarterLength=q


        new_elements.append(el)



        total += q



    # 不足補休止

    if total < TARGET_BEATS:


        remain=TARGET_BEATS-total


        r=make_rest(remain)


        new_elements.append(r)


        total += remain



    # 清除原內容

    measure.clear()


    for e in new_elements:

        measure.append(e)



    return total



# ==========================================================
# Main
# ==========================================================

def main():

    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python jianpu_safe_fix.py input.musicxml output.musicxml"
        )

        sys.exit()



    src=sys.argv[1]

    out=sys.argv[2]



    print(
        "讀取 MusicXML..."
    )


    score=converter.parse(src)



    print(
        "修正小節..."
    )



    fixed=stream.Score()



    for part in score.parts:


        new_part=stream.Part()


        for m in part.getElementsByClass(
            stream.Measure
        ):


            nm=copy.deepcopy(m)


            beats=fix_measure(nm)


            print(
                f"Measure {nm.number}: {beats}"
            )


            new_part.append(nm)



        fixed.append(new_part)



    print(
        "輸出:"
    )


    fixed.write(
        "musicxml",
        fp=out
    )


    print(
        "完成:",
        out
    )



if __name__=="__main__":

    main()