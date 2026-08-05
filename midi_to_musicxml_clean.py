# ==========================================================
# midi_to_musicxml_clean.py V29
#
# JianpuTool
# MIDI -> MusicXML
#
# Features:
# 1. Auto detect Vocal MIDI
# 2. Auto detect Melody / Lead track
# 3. Fallback single track melody extraction
# 4. Clean melody output
#
# ==========================================================

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import instrument
from music21 import meter
from music21 import tempo


# ----------------------------------------------------------
# 找 Vocal Track
# ----------------------------------------------------------

VOCAL_KEYS = [
    "vocal",
    "voice",
    "melody",
    "lead",
    "singer",
    "sing"
]


def find_vocal_part(score):

    for part in score.parts:

        name = ""

        if part.partName:
            name = str(part.partName).lower()


        if any(k in name for k in VOCAL_KEYS):

            print(
                "找到 Vocal Track:",
                part.partName
            )

            return part


    return None



# ----------------------------------------------------------
# 分析音域
# ----------------------------------------------------------

def get_notes(part):

    return [
        n for n in part.recurse().notes
        if isinstance(n, note.Note)
    ]



# ----------------------------------------------------------
# 單軌 MIDI 抽主旋律
# ----------------------------------------------------------

def extract_melody(part):

    print("啟動 Melody Extractor")


    notes = []

    for n in part.recurse().notes:

        if isinstance(n, note.Note):

            notes.append(n)

        elif isinstance(n, chord.Chord):

            # 保留最高音
            highest = max(
                n.notes,
                key=lambda x:x.pitch.midi
            )

            notes.append(highest)


    # 排除低音
    filtered = [
        n for n in notes
        if n.pitch.midi >= 48
    ]


    print(
        "原始音符:",
        len(notes)
    )

    print(
        "保留旋律:",
        len(filtered)
    )


    new_part = stream.Part()

    for n in filtered:

        new_part.append(
            copy.deepcopy(n)
        )


    return new_part



# ----------------------------------------------------------
# 建立4/4小節
# ----------------------------------------------------------

def rebuild_measures(part):

    result = stream.Part()


    result.append(
        meter.TimeSignature("4/4")
    )


    result.append(
        tempo.MetronomeMark(
            number=80
        )
    )


    for n in part.notes:

        result.append(n)


    return result



# ----------------------------------------------------------
# main
# ----------------------------------------------------------

if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用:"
        )

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit()


    midi_file = sys.argv[1]

    output = sys.argv[2]


    print("讀取 MIDI...")


    score = converter.parse(
        midi_file
    )


    print(
        "Tracks:",
        len(score.parts)
    )



    # -------------------------
    # Step 1 Vocal
    # -------------------------

    vocal = find_vocal_part(score)


    if vocal:

        print(
            "模式: Vocal MIDI"
        )

        melody = copy.deepcopy(vocal)



    else:

        print(
            "沒有 Vocal Track"
        )


        if len(score.parts) == 1:

            print(
                "模式: 單軌 MIDI"
            )

            melody = extract_melody(
                score.parts[0]
            )


        else:

            print(
                "模式: 多軌搜尋最高旋律"
            )


            best = None
            best_count = 0


            for part in score.parts:

                count = len(
                    get_notes(part)
                )


                if count > best_count:

                    best_count = count
                    best = part


            melody = extract_melody(best)



    # -------------------------
    # 建立 MusicXML
    # -------------------------

    print(
        "建立 MusicXML..."
    )


    final_score = stream.Score()


    final_score.append(
        rebuild_measures(melody)
    )


    final_score.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )