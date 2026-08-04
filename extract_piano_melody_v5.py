from mido import MidiFile, MidiTrack, Message, MetaMessage
import sys


if len(sys.argv) < 3:
    print("usage:")
    print("python extract_piano_melody_v5.py input.mid output.mid")
    exit()


src = sys.argv[1]
dst = sys.argv[2]


print("LOAD:", src)


mid = MidiFile(src)


# =========================
# 讀取 MIDI note
# =========================

notes = []


for track in mid.tracks:

    abs_time = 0
    active = {}


    for msg in track:

        abs_time += msg.time


        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = (
                abs_time,
                msg.velocity
            )


        elif (
            msg.type == "note_off"
            or
            (msg.type == "note_on" and msg.velocity == 0)
        ):

            if msg.note in active:

                start, vel = active[msg.note]

                notes.append(
                    {
                        "note": msg.note,
                        "start": start,
                        "duration": abs_time-start,
                        "velocity": vel
                    }
                )

                del active[msg.note]



print("TOTAL NOTES:", len(notes))


if not notes:
    print("ERROR: no notes")
    exit()



# =========================
# 去除低音
# =========================

notes = [
    n for n in notes
    if n["note"] >= 55
]


print("REMOVE BASS:", len(notes))



# =========================
# 排序
# =========================

notes.sort(
    key=lambda x:x["start"]
)



# =========================
# 同時間多音
# 只留最高音
# =========================

melody=[]


i=0


while i < len(notes):

    group=[]

    t=notes[i]["start"]


    while (
        i < len(notes)
        and notes[i]["start"] == t
    ):
        group.append(notes[i])
        i += 1



    highest=max(
        group,
        key=lambda x:x["note"]
    )


    melody.append(highest)



print(
    "MELODY NOTES:",
    len(melody)
)



# =========================
# 建立新的 MIDI
# =========================

out=MidiFile(
    type=1,
    ticks_per_beat=480
)


track=MidiTrack()

out.tracks.append(track)



track.append(
    MetaMessage(
        "time_signature",
        numerator=4,
        denominator=4,
        time=0
    )
)


track.append(
    MetaMessage(
        "set_tempo",
        tempo=500000,
        time=0
    )
)



# =========================
# 重新排列旋律
# 每個音固定一拍
# =========================


for n in melody:


    track.append(
        Message(
            "note_on",
            note=n["note"],
            velocity=90,
            time=0
        )
    )


    track.append(
        Message(
            "note_off",
            note=n["note"],
            velocity=0,
            time=480
        )
    )



# 結尾

track.append(
    MetaMessage(
        "end_of_track",
        time=0
    )
)



out.save(dst)



print()
print("DONE:")
print(dst)