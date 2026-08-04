#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> Clean MusicXML V3.1 melody extract
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
# 抽取主旋律
# -----------------------------

def extract_melody(part):

    result = stream.Part()


    print("分析右手旋律...")


    for n in part.flatten().notes:


        # 單音

        if isinstance(
            n,
            note.Note
        ):


            # 鋼琴右手通常 C4以上

            if n.pitch.midi >= 60:

                result.append(
                    copy.deepcopy(n)
                )



        # 和弦

        elif isinstance(
            n,
            chord.Chord
        ):


            # 取最高音

            highest = max(
                n.pitches,
                key=lambda x:x.midi
            )


            new_note = note.Note(
                highest
            )


            new_note.duration = copy.deepcopy(
                n.duration
            )


            result.append(
                new_note
            )



    return result




# -----------------------------
# 移除太短音符
# -----------------------------

def remove_noise(part):

    result = stream.Part()


    for n in part.notes:


        if n.duration.quarterLength < 0.15:

            continue


        result.append(
            n
        )


    return result




# -----------------------------
# 修正小節長度
# -----------------------------

def fix_measures(part):

    new_part = stream.Part()


    new_part.append(
        meter.TimeSignature("4/4")
    )


    current = 0



    for n in part.flatten().notesAndRests:


        dur = quantize(
            n.duration.quarterLength
        )


        if dur <= 0:

            continue



        obj = copy.deepcopy(n)


        obj.duration.quarterLength = dur



        # 超過4拍

        if current + dur > 4:


            remain = 4-current


            if remain > 0:


                rest = note.Rest()

                rest.duration.quarterLength = remain

                new_part.append(rest)



            current = 0



        new_part.append(
            obj
        )


        current += dur



        if abs(current-4)<0.001:

            current = 0




    # 補尾

    if current > 0:


        rest = note.Rest()

        rest.duration.quarterLength = 4-current

        new_part.append(
            rest
        )



    return new_part




# -----------------------------
# 主程式
# -----------------------------

def process():


    print("讀取 MIDI...")


    score = converter.parse(
        INPUT,
        format="midi"
    )



    print("取得鋼琴 Part...")


    # 保留 V3.0 成功方式

    part = score.parts[0]



    print("抽取旋律...")


    part = extract_melody(
        part
    )



    print("移除雜訊...")


    part = remove_noise(
        part
    )



    print("修正小節...")


    clean_part = fix_measures(
        part
    )



    score_out = stream.Score()



    score_out.append(
        tempo.MetronomeMark(
            number=80
        )
    )


    score_out.append(
        clean_part
    )



    print("輸出 MusicXML...")


    score_out.write(
        "musicxml",
        fp=OUTPUT
    )


    print(
        "完成:",
        OUTPUT
    )




if __name__=="__main__":

    process()