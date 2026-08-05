# ==========================================
# MIDI NOTE FILTER V6
#
# BasicPitch MIDI Cleaner
#
# Input:
#   raw.mid
#
# Output:
#   melody_clean.mid
#
# Features:
#   - remove extreme pitch
#   - remove short notes
#   - keep melody line
#   - monophonic extraction
#   - quantize
# ==========================================


import sys
from music21 import converter, stream, note, chord
from music21 import tempo


# ==============================
# Settings
# ==============================

LOW_NOTE = 45     # A2
HIGH_NOTE = 84    # C6

MIN_DURATION = 0.08


# ==============================
# Quantize
# ==============================

def quantize_time(value):

    # 16分音符

    return round(value * 4) / 4



# ==============================
# Main filter
# ==============================

def filter_midi(src, dst):


    print("==============================")
    print(" MIDI NOTE FILTER V6")
    print("==============================")


    print("讀取 MIDI...")

    midi = converter.parse(src)



    notes = []


    for n in midi.flatten().notes:


        # chord 拆開

        if isinstance(n, chord.Chord):


            for p in n.pitches:


                if (
                    LOW_NOTE <= p.midi <= HIGH_NOTE
                ):

                    notes.append(
                        note.Note(
                            p,
                            quarterLength=n.quarterLength
                        )
                    )



        elif isinstance(n, note.Note):


            if (
                LOW_NOTE <= n.pitch.midi <= HIGH_NOTE
            ):

                notes.append(
                    n
                )



    print(
        "音符數(篩選前):",
        len(notes)
    )



    # ==============================
    # 移除短音
    # ==============================

    clean = []


    for n in notes:


        if n.duration.quarterLength >= MIN_DURATION:

            clean.append(n)



    print(
        "移除短音後:",
        len(clean)
    )



    # ==============================
    # 同時間只留最高音
    # ==============================

    groups = {}


    for n in clean:


        key = round(
            n.offset,
            3
        )


        if key not in groups:

            groups[key] = n

        else:

            if (
                n.pitch.midi >
                groups[key].pitch.midi
            ):

                groups[key] = n



    melody = list(
        groups.values()
    )


    melody.sort(
        key=lambda x:x.offset
    )



    print(
        "旋律音符:",
        len(melody)
    )



    # ==============================
    # 建立新 MIDI
    # ==============================

    out = stream.Stream()



    part = stream.Part()


    part.insert(
        0,
        tempo.MetronomeMark(
            number=80
        )
    )



    for n in melody:


        new = note.Note(
            n.pitch
        )


        new.duration.quarterLength = (
            quantize_time(
                n.duration.quarterLength
            )
        )


        part.insert(
            quantize_time(
                n.offset
            ),
            new
        )



    out.insert(
        0,
        part
    )


    out.write(
        "midi",
        fp=dst
    )



    print()
    print(
        "完成:",
        dst
    )



# ==============================
# Run
# ==============================


if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "用法:"
        )

        print(
            "python midi_note_filter_v6.py input.mid output.mid"
        )

        sys.exit()



    filter_midi(
        sys.argv[1],
        sys.argv[2]
    )