#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> MusicXML Clean V3.1
#

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import note
from music21 import tempo



INPUT = sys.argv[1]
OUTPUT = sys.argv[2]



# =========================
# 量化
# =========================

def quantize(value):

    # 16分音符
    return round(value * 4) / 4



# =========================
# 自動選旋律
# =========================

def choose_melody(score):

    best = None
    best_value = -1


    for part in score.parts:

        notes = list(
            part.flat.notes
        )


        if len(notes) == 0:
            continue


        count = len(notes)


        avg_pitch = sum(
            n.pitch.midi
            for n in notes
        ) / count


        # 高音 + 音符數量
        value = count + avg_pitch * 2


        if value > best_value:

            best_value = value
            best = part



    return best




# =========================
# 移除低音伴奏
# =========================

def remove_low_notes(part):

    result = stream.Part()


    for n in part.flat.notes:


        if n.pitch.midi < 55:

            continue


        result.append(
            n
        )


    return result




# =========================
# 移除雜訊
# =========================

def remove_noise(part):

    result = stream.Part()


    for n in part.flat.notes:


        if n.duration.quarterLength < 0.15:

            continue


        result.append(
            n
        )


    return result




# =========================
# 合併同時間重複音
# =========================

def remove_duplicate_notes(part):

    result = stream.Part()


    last_pitch = None
    last_offset = -1


    for n in part.notes:


        if (
            n.pitch.midi == last_pitch
            and
            abs(n.offset-last_offset)<0.01
        ):

            continue


        result.append(n)


        last_pitch = n.pitch.midi
        last_offset = n.offset



    return result




# =========================
# 修正小節
# =========================

def rebuild_measure(part):

    result = stream.Part()


    result.append(
        meter.TimeSignature("4/4")
    )


    current = 0


    for n in part.flat.notes:


        obj = copy.deepcopy(n)


        dur = quantize(
            obj.duration.quarterLength
        )


        if dur <= 0:
            continue


        obj.duration.quarterLength = dur



        if current + dur > 4:


            rest = note.Rest()


            rest.duration.quarterLength = (
                4-current
            )


            if rest.duration.quarterLength > 0:

                result.append(rest)


            current = 0



        result.append(obj)


        current += dur



        if abs(current-4)<0.001:

            current=0




    # 補尾端

    if current>0:


        rest = note.Rest()

        rest.duration.quarterLength = 4-current

        result.append(rest)



    return result




# =========================
# 主程式
# =========================

def main():


    print("讀取 MIDI")

    score = converter.parse(
        INPUT,
        format="midi"
    )



    print("選擇主旋律")

    part = choose_melody(score)



    if part is None:

        raise Exception(
            "找不到旋律"
        )



    print("移除低音")

    part = remove_low_notes(part)



    print("移除雜訊")

    part = remove_noise(part)



    print("去除重複音")

    part = remove_duplicate_notes(part)



    print("重建小節")

    part = rebuild_measure(part)



    output = stream.Score()


    output.append(
        tempo.MetronomeMark(
            number=84
        )
    )


    output.append(
        part
    )



    print("輸出 MusicXML")

    output.write(
        "musicxml",
        fp=OUTPUT
    )


    print(
        "完成:",
        OUTPUT
    )



if __name__=="__main__":

    main()