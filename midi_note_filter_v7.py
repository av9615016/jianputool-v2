# ==========================================
# MIDI NOTE FILTER V7
#
# BasicPitch Vocal Melody Cleaner
#
# Input:
#   raw.mid
#
# Output:
#   melody_clean.mid
#
# ==========================================


import sys
from music21 import converter, stream, note, chord
from music21 import tempo


# ==========================
# Settings
# ==========================

LOW_NOTE = 45       # A2
HIGH_NOTE = 84      # C6

MIN_DURATION = 0.15

MIN_GAP = 0.08

MAX_JUMP = 24



# ==========================
# Filter
# ==========================


def filter_midi(src, dst):


    print("==============================")
    print(" MIDI NOTE FILTER V7")
    print("==============================")


    print("讀取 MIDI...")


    score = converter.parse(src)



    raw_notes = []



    for n in score.flatten().notes:


        if isinstance(n, chord.Chord):


            # chord 留最高音

            p = max(
                n.pitches,
                key=lambda x:x.midi
            )


            if LOW_NOTE <= p.midi <= HIGH_NOTE:

                new = note.Note(
                    p
                )

                new.offset = n.offset
                new.duration = n.duration

                raw_notes.append(new)



        elif isinstance(n, note.Note):


            pitch = n.pitch.midi


            if LOW_NOTE <= pitch <= HIGH_NOTE:

                raw_notes.append(
                    n
                )



    print(
        "音符:",
        len(raw_notes)
    )



    # ==========================
    # duration filter
    # ==========================


    notes = []


    for n in raw_notes:


        if n.duration.quarterLength >= MIN_DURATION:

            notes.append(n)



    print(
        "長音保留:",
        len(notes)
    )



    # ==========================
    # same time highest
    # ==========================


    timeline = {}


    for n in notes:


        key = round(
            n.offset,
            2
        )


        if key not in timeline:

            timeline[key] = n


        else:


            if n.pitch.midi > timeline[key].pitch.midi:

                timeline[key] = n



    notes = list(
        timeline.values()
    )


    notes.sort(
        key=lambda x:x.offset
    )



    print(
        "單音化:",
        len(notes)
    )



    # ==========================
    # melody tracking
    # ==========================


    melody = []


    last = None
    last_time = -1



    for n in notes:


        pitch = n.pitch.midi


        # 第一個音

        if last is None:

            melody.append(n)

            last = pitch
            last_time = n.offset

            continue



        jump = abs(
            pitch - last
        )


        gap = (
            n.offset - last_time
        )



        # 太大跳音

        if jump > MAX_JUMP:

            continue



        # 太密集

        if gap < MIN_GAP:

            continue



        melody.append(n)

        last = pitch
        last_time = n.offset



    print(
        "旋律追蹤:",
        len(melody)
    )



    # ==========================
    # output midi
    # ==========================


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
            n.duration.quarterLength
        )


        part.insert(
            n.offset,
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



# ==========================
# Main
# ==========================


if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用:"
        )

        print(
            "python midi_note_filter_v7.py input.mid output.mid"
        )

        sys.exit()



    filter_midi(
        sys.argv[1],
        sys.argv[2]
    )