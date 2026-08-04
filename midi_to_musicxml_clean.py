#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> Clean MusicXML V3.0
#

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import note
from music21 import chord
from music21 import tempo



INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


# -----------------------------
# 16分音符量化
# -----------------------------

def quantize(value):

    return round(value * 4) / 4



# -----------------------------
# 移除太短音符
# -----------------------------

def remove_noise(part):

    result = stream.Part()

    for n in part.notes:

        if n.duration.quarterLength < 0.15:
            continue

        result.append(n)

    return result



# -----------------------------
# 修正小節長度
# -----------------------------

def fix_measures(part):

    new_part = stream.Part()

    ts = meter.TimeSignature("4/4")
    new_part.append(ts)


    current = 0


    for n in part.flat.notesAndRests:


        dur = quantize(n.duration.quarterLength)


        if dur <= 0:
            continue


        obj = copy.deepcopy(n)

        obj.duration.quarterLength = dur


        # 超過小節
        if current + dur > 4:

            remain = 4 - current


            if remain > 0:

                rest = note.Rest()
                rest.duration.quarterLength = remain
                new_part.append(rest)


            current = 0


        new_part.append(obj)

        current += dur



        # 小節完成

        if abs(current - 4) < 0.001:

            current = 0



    # 補最後小節

    if current > 0:

        rest = note.Rest()
        rest.duration.quarterLength = 4-current
        new_part.append(rest)



    return new_part



# -----------------------------
# 建立 Score
# -----------------------------

def process():

    print("讀取 MIDI...")

    score = converter.parse(
        INPUT,
        format="midi"
    )


    print("取得主旋律...")


    part = score.parts[0]


    # 移除雜訊

    part = remove_noise(part)



    print("量化節奏...")


    clean_part = fix_measures(part)



    score_out = stream.Score()

    score_out.append(
        tempo.MetronomeMark(
            number=80
        )
    )


    score_out.append(clean_part)



    print("輸出 MusicXML...")


    score_out.write(
        "musicxml",
        fp=OUTPUT
    )


    print("完成:")
    print(OUTPUT)



if __name__ == "__main__":

    process()