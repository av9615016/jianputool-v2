# ==========================================================
# midi_to_musicxml_clean.py V30
#
# JianpuTool
#
# MIDI -> MusicXML
#
# Melody Extractor Pro
#
# ==========================================================

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo


# ----------------------------------------------------------
# Vocal Track 偵測
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
# Melody Extractor Pro
# ----------------------------------------------------------

def extract_melody_pro(part):

    print("啟動 Melody Extractor Pro")


    raw = []


    # 收集所有 note

    for element in part.recurse().notes:

        if isinstance(element, note.Note):

            raw.append(
                copy.deepcopy(element)
            )


        elif isinstance(element, chord.Chord):

            # chord只取最高音

            highest = max(
                element.notes,
                key=lambda x:x.pitch.midi
            )

            raw.append(
                copy.deepcopy(highest)
            )


    print(
        "原始音符:",
        len(raw)
    )


    # ------------------------------
    # 1. 排除低音
    # ------------------------------

    raw = [
        n for n in raw
        if n.pitch.midi >= 55
    ]


    print(
        "移除低音後:",
        len(raw)
    )


    # ------------------------------
    # 2. 同時間保留最高音
    # ------------------------------

    timeline = {}


    for n in raw:

        key = round(
            float(n.offset),
            3
        )


        if key not in timeline:

            timeline[key] = n

        else:

            if n.pitch.midi > timeline[key].pitch.midi:

                timeline[key] = n



    melody = list(
        timeline.values()
    )


    melody.sort(
        key=lambda x:x.offset
    )


    print(
        "時間去重後:",
        len(melody)
    )


    # ------------------------------
    # 3. 移除極短裝飾音
    # ------------------------------

    cleaned = []


    for n in melody:

        if n.duration.quarterLength >= 0.25:

            cleaned.append(n)



    print(
        "節奏過濾後:",
        len(cleaned)
    )


    # ------------------------------
    # 建立新 Part
    # ------------------------------

    result = stream.Part()


    for n in cleaned:

        result.append(
            n
        )


    return result



# ----------------------------------------------------------
# 建立基本樂譜
# ----------------------------------------------------------

def build_score(part):

    score = stream.Score()


    new_part = stream.Part()


    new_part.append(
        meter.TimeSignature("4/4")
    )


    new_part.append(
        tempo.MetronomeMark(
            number=80
        )
    )


    for n in part.notes:

        new_part.append(
            n
        )


    score.append(
        new_part
    )


    return score



# ----------------------------------------------------------
# MAIN
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



    # --------------------------
    # Vocal 優先
    # --------------------------

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


        # 單軌

        if len(score.parts) == 1:

            melody = extract_melody_pro(
                score.parts[0]
            )


        else:

            print(
                "多軌搜尋最佳旋律"
            )


            best = None

            best_score = 0


            for part in score.parts:

                count = len(
                    [
                        n for n in part.recurse().notes
                    ]
                )


                if count > best_score:

                    best_score = count
                    best = part



            melody = extract_melody_pro(
                best
            )



    print(
        "建立 MusicXML..."
    )


    final = build_score(
        melody
    )


    final.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )