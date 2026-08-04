#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> MusicXML Clean V3.1.1
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



# =========================
# 16分音符量化
# =========================

def quantize(value):

    return round(value * 4) / 4



# =========================
# 自動選旋律軌
# =========================

def choose_melody(score):

    best_part = None
    best_value = -1


    for part in score.parts:


        notes = list(
            part.flatten().notes
        )


        if len(notes) == 0:
            continue



        pitches = []


        for n in notes:


            if isinstance(
                n,
                note.Note
            ):


                pitches.append(
                    n.pitch.midi
                )


            elif isinstance(
                n,
                chord.Chord
            ):


                pitches.append(
                    max(
                        p.midi
                        for p in n.pitches
                    )
                )



        if len(pitches)==0:
            continue



        avg_pitch = (
            sum(pitches)
            /
            len(pitches)
        )



        count = len(notes)



        # 高音 + 音符數量
        value = (
            count
            +
            avg_pitch * 2
        )



        if value > best_value:

            best_value = value
            best_part = part



    return best_part




# =========================
# 移除低音伴奏
# =========================

def remove_low_notes(part):

    result = stream.Part()



    for n in part.flatten().notes:


        keep = True



        if isinstance(
            n,
            note.Note
        ):


            if n.pitch.midi < 55:

                keep = False



        elif isinstance(
            n,
            chord.Chord
        ):


            high = max(
                p.midi
                for p in n.pitches
            )


            if high < 55:

                keep = False




        if keep:

            result.append(
                n
            )



    return result




# =========================
# 移除太短音
# =========================

def remove_noise(part):

    result = stream.Part()



    for n in part.notes:


        if (
            n.duration.quarterLength
            < 0.15
        ):

            continue



        result.append(
            n
        )



    return result




# =========================
# 和弦取最高音
# =========================

def chord_to_note(part):

    result = stream.Part()



    for n in part.flatten().notes:


        if isinstance(
            n,
            chord.Chord
        ):


            new_note = note.Note(
                max(
                    n.pitches
                )
            )


            new_note.duration = (
                copy.deepcopy(
                    n.duration
                )
            )


            result.append(
                new_note
            )


        else:

            result.append(
                n
            )



    return result




# =========================
# 去除重複音
# =========================

def remove_duplicate_notes(part):

    result = stream.Part()


    last_pitch = None
    last_offset = -1



    for n in part.notes:


        if not isinstance(
            n,
            note.Note
        ):

            continue



        if (
            n.pitch.midi == last_pitch
            and
            abs(
                n.offset-last_offset
            )
            <0.01
        ):

            continue



        result.append(
            n
        )


        last_pitch = n.pitch.midi
        last_offset = n.offset



    return result




# =========================
# 重建4/4小節
# =========================

def rebuild_measure(part):

    result = stream.Part()


    result.append(
        meter.TimeSignature(
            "4/4"
        )
    )


    current = 0



    for n in part.notes:


        obj = copy.deepcopy(n)



        dur = quantize(
            obj.duration.quarterLength
        )



        if dur <=0:
            continue



        obj.duration.quarterLength = dur



        if current + dur > 4:


            rest = note.Rest()


            rest.duration.quarterLength = (
                4-current
            )


            if rest.duration.quarterLength >0:

                result.append(
                    rest
                )


            current=0



        result.append(
            obj
        )


        current += dur



        if abs(current-4)<0.001:

            current=0




    if current>0:


        rest = note.Rest()

        rest.duration.quarterLength = (
            4-current
        )

        result.append(
            rest
        )



    return result




# =========================
# Main
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
            "沒有找到音符"
        )



    print("移除低音")

    part = remove_low_notes(
        part
    )



    print("和弦轉單音")

    part = chord_to_note(
        part
    )



    print("移除雜訊")

    part = remove_noise(
        part
    )



    print("去除重複音")

    part = remove_duplicate_notes(
        part
    )



    print("重建小節")

    part = rebuild_measure(
        part
    )



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