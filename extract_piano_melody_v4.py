# extract_piano_melody_v4.py
# JianpuTool Melody Extractor V4
# MIDI piano -> single melody MIDI

import sys
import mido
from mido import MidiFile, MidiTrack, Message


if len(sys.argv) < 3:
    print("Usage:")
    print("python extract_piano_melody_v4.py input.mid output.mid")
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("LOAD:", input_file)


mid = MidiFile(input_file)


ticks_per_beat = mid.ticks_per_beat


# 收集所有 note event
events = []

current_time = 0


for track in mid.tracks:

    abs_time = 0
    active = {}

    for msg in track:

        abs_time += msg.time

        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = abs_time


        elif msg.type in ["note_off", "note_on"]:

            if msg.note in active:

                start = active[msg.note]

                duration = abs_time - start

                events.append(
                    {
                        "start": start,
                        "note": msg.note,
                        "duration": duration,
                        "velocity": msg.velocity
                    }
                )

                del active[msg.note]


print("TOTAL NOTES:", len(events))


# ------------------------------------------------
# 1. 移除低音
# C4 = 60
# ------------------------------------------------

melody_candidates = []

for e in events:

    if e["note"] >= 60:

        melody_candidates.append(e)


print(
    "REMOVE BASS:",
    len(events),
    "->",
    len(melody_candidates)
)


# ------------------------------------------------
# 2. 同時間只留最高音
# ------------------------------------------------

groups = {}


for e in melody_candidates:

    t = e["start"]

    if t not in groups:
        groups[t] = []

    groups[t].append(e)



melody = []


for t in sorted(groups):

    notes = groups[t]

    # 取最高音
    top = max(
        notes,
        key=lambda x:x["note"]
    )

    melody.append(top)


print(
    "MELODY NOTES:",
    len(melody)
)



# ------------------------------------------------
# 3. 建立新 MIDI
# ------------------------------------------------


out = MidiFile(
    ticks_per_beat=ticks_per_beat
)


track = MidiTrack()

out.tracks.append(track)


last_time = 0


for e in melody:

    delta = e["start"] - last_time


    track.append(
        Message(
            "note_on",
            note=e["note"],
            velocity=90,
            time=delta
        )
    )


    track.append(
        Message(
            "note_off",
            note=e["note"],
            velocity=0,
            time=e["duration"]
        )
    )


    last_time = e["start"] + e["duration"]



out.save(output_file)


print()
print("DONE:")
print(output_file)