#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> MusicXML Clean V3.2.1 FINAL
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



# -------------------------
# 量化
# -------------------------

def quantize(x):

    return round(x * 4) / 4



# -------------------------
# 選旋律
# -------------------------

def choose_melody(score):

    best = None
    best_score = -1


    for p in score.parts:


        notes = list(
            p.flatten().notes
        )


        if not notes:
            continue


        pitches=[]


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
                        x.midi
                        for x in n.pitches
                    )
                )


        if not pitches:
            continue


        avg = sum(pitches)/len(pitches)


        score_value = (
            len(notes)
            +
            avg*2
        )


        if score_value > best_score:

            best_score = score_value
            best = p



    return best




# -------------------------
# chord轉最高音
# -------------------------

def chord_to_note(part):

    result = stream.Part()


    for n in part.flatten().notes:


        if isinstance(
            n,
            chord.Chord
        ):


            new_note = note.Note(
                max(n.pitches)
            )


            new_note.duration = copy.deepcopy(
                n.duration
            )


            result.append(
                new_note
            )


        else:

            result.append(
                n
            )


    return result




# -------------------------
# 移除低音
# -------------------------

def remove_low_notes(part):

    result = stream.Part()


    for n in part.notes:


        if n.pitch.midi < 55:

            continue


        result.append(
            n
        )


    return result




# -------------------------
# 移除雜訊
# -------------------------

def remove_noise(part):

    result = stream.Part()


    for n in part.notes:


        if n.duration.quarterLength < 0.15:

            continue


        result.append(n)


    return result




# -------------------------
# 去重複
# -------------------------

def remove_duplicate(part):

    result = stream.Part()


    last_pitch = None
    last_offset = None


    for n in part.notes:


        if (
            n.pitch.midi == last_pitch
            and
            n.offset == last_offset
        ):

            continue


        result.append(n)


        last_pitch = n.pitch.midi
        last_offset = n.offset



    return result




# -------------------------
# 建立真正Measure
# -------------------------

def rebuild_measures(part):


    new_part = stream.Part()


    new_part.append(
        meter.TimeSignature("4/4")
    )


    measure_number = 1


    m = stream.Measure(
        number=measure_number
    )


    beat = 0



    for n in part.notes:


        obj = copy.deepcopy(n)


        dur = quantize(
            obj.duration.quarterLength
        )


        if dur <=0:

            continue



        obj.duration.quarterLength = dur



        # 超過4拍切割

        if beat + dur > 4:


            remain = 4-beat


            if remain > 0:


                r = note.Rest()

                r.duration.quarterLength = remain

                m.append(r)



            new_part.append(m)


            measure_number += 1


            m = stream.Measure(
                number=measure_number
            )


            beat = 0




        m.append(obj)


        beat += dur




        if beat >=4:


            new_part.append(m)


            measure_number +=1


            m = stream.Measure(
                number=measure_number
            )


            beat=0




    # 最後補滿

    if len(m.notesAndRests)>0:


        if beat <4:


            r = note.Rest()

            r.duration.quarterLength = (
                4-beat
            )

            m.append(r)



        new_part.append(m)



    return new_part




# -------------------------
# Main
# -------------------------

def main():


    print("讀取 MIDI")


    score = converter.parse(
        INPUT,
        format="midi"
    )



    print("選擇旋律")

    part = choose_melody(score)



    if part is None:

        raise Exception(
            "找不到旋律"
        )



    print("Chord轉單音")

    part = chord_to_note(part)



    print("移除低音")

    part = remove_low_notes(part)



    print("移除雜訊")

    part = remove_noise(part)



    print("去重複")

    part = remove_duplicate(part)



    print("建立Measure")

    part = rebuild_measures(part)



    # -----------------
    # 建立Score
    # -----------------

    output = stream.Score()



    output.append(
        tempo.MetronomeMark(
            number=84
        )
    )


    output.append(
        part
    )



    print("重新整理小節")


    output.makeMeasures(
        inPlace=True
    )



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