#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> Clean MusicXML V3.1 FINAL
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
# 自動選主旋律
# -----------------------------

def choose_melody(score):

    best_part = None
    best_score = -1


    for p in score.parts:


        notes = list(
            p.flatten().notes
        )


        if len(notes) == 0:
            continue



        pitch_sum = 0
        count = 0



        for n in notes:


            if isinstance(
                n,
                note.Note
            ):

                pitch_sum += n.pitch.midi
                count += 1



            elif isinstance(
                n,
                chord.Chord
            ):

                pitch_sum += max(
                    x.midi
                    for x in n.pitches
                )

                count += 1



        if count == 0:
            continue



        avg_pitch = pitch_sum / count



        value = (
            len(notes)
            +
            avg_pitch * 2
        )


        print(
            "Part:",
            p.id,
            "Notes:",
            len(notes),
            "AvgPitch:",
            avg_pitch
        )



        if value > best_score:

            best_score = value
            best_part = p



    return best_part





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



    for n in part.flatten().notesAndRests:


        dur = quantize(
            n.duration.quarterLength
        )


        if dur <= 0:

            continue



        obj = copy.deepcopy(n)


        obj.duration.quarterLength = dur




        if current + dur > 4:


            remain = 4-current


            if remain > 0:


                rest = note.Rest()

                rest.duration.quarterLength = remain

                new_part.append(rest)



            current = 0




        new_part.append(obj)


        current += dur



        if abs(current-4)<0.001:

            current=0




    if current > 0:


        rest = note.Rest()

        rest.duration.quarterLength = 4-current

        new_part.append(rest)



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



    print("自動選擇主旋律...")


    part = choose_melody(score)



    if part is None:

        raise Exception(
            "找不到旋律"
        )



    print("移除雜訊...")


    part = remove_noise(part)




    print("量化節奏...")


    clean_part = fix_measures(part)



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




if __name__ == "__main__":

    process()