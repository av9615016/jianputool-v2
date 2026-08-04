#
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> MusicXML Clean V3.2 FINAL
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
# 量化
# =========================

def quantize(value):

    # 16分音符
    return round(value * 4) / 4



# =========================
# 選旋律軌
# =========================

def choose_melody(score):

    best = None
    best_score = -1


    for part in score.parts:


        notes = list(
            part.flatten().notes
        )


        if not notes:
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



        if not pitches:
            continue



        avg = sum(pitches) / len(pitches)


        value = (
            len(notes)
            +
            avg * 2
        )



        if value > best_score:

            best_score = value
            best = part



    return best




# =========================
# 和弦轉最高音
# =========================

def chord_to_note(part):

    result = stream.Part()



    for n in part.flatten().notes:


        if isinstance(
            n,
            chord.Chord
        ):


            new = note.Note(
                max(n.pitches)
            )


            new.duration = copy.deepcopy(
                n.duration
            )


            result.append(new)



        else:

            result.append(
                n
            )



    return result




# =========================
# 去低音
# =========================

def remove_low_notes(part):

    result = stream.Part()



    for n in part.notes:


        if n.pitch.midi < 55:

            continue


        result.append(
            n
        )



    return result




# =========================
# 去雜訊
# =========================

def remove_noise(part):

    result = stream.Part()


    for n in part.notes:


        if n.duration.quarterLength < 0.15:

            continue


        result.append(n)



    return result




# =========================
# 去重複音
# =========================

def remove_duplicate(part):

    result = stream.Part()


    last_pitch = None
    last_time = None



    for n in part.notes:


        if (
            last_pitch == n.pitch.midi
            and
            last_time == n.offset
        ):

            continue



        result.append(n)


        last_pitch = n.pitch.midi
        last_time = n.offset



    return result




# =========================
# 建立真正 Measure
# =========================

def rebuild_measures(part):


    result = stream.Part()


    result.append(
        meter.TimeSignature("4/4")
    )


    measure_no = 1


    m = stream.Measure(
        number=measure_no
    )


    beat = 0



    for n in part.notes:


        obj = copy.deepcopy(n)


        dur = quantize(
            obj.duration.quarterLength
        )


        if dur <= 0:
            continue



        obj.duration.quarterLength = dur



        # 超過小節

        if beat + dur > 4:


            remain = 4-beat


            if remain > 0:


                r = note.Rest()

                r.duration.quarterLength = remain

                m.append(r)



            result.append(m)



            measure_no += 1


            m = stream.Measure(
                number=measure_no
            )


            beat = 0




        m.append(obj)


        beat += dur




        # 完整小節

        if abs(beat-4)<0.001:


            result.append(m)


            measure_no += 1


            m = stream.Measure(
                number=measure_no
            )


            beat = 0




    # 最後小節

    if len(m.notesAndRests)>0:


        if beat < 4:


            r = note.Rest()

            r.duration.quarterLength = (
                4-beat
            )

            m.append(r)



        result.append(m)



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



    print("選擇旋律")


    part = choose_melody(score)



    if part is None:

        raise Exception(
            "沒有找到旋律"
        )



    print("Chord轉單音")

    part = chord_to_note(part)



    print("移除低音")

    part = remove_low_notes(part)



    print("移除雜訊")

    part = remove_noise(part)



    print("去重複")

    part = remove_duplicate(part)



    print("建立4/4小節")

    part = rebuild_measures(part)



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



if __name__ == "__main__":

    main()