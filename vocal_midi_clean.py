# vocal_midi_clean.py
#
# JianpuTool
# Vocal MIDI Cleaner V1.0
#
# BasicPitch Vocal MIDI
#        |
#        v
# Clean Vocal Melody MIDI
#

import sys
from music21 import converter, note, stream


# ==========================
# 設定
# ==========================

LOW_NOTE = 40        # E2 以下通常不是主唱
MIN_DURATION = 0.08  # 秒
MERGE_GAP = 0.08     # 合併間隔


# ==========================
# 主程式
# ==========================

if len(sys.argv) < 3:
    print(
        "使用方式:\n"
        "python vocal_midi_clean.py input.mid output.mid"
    )
    sys.exit()


input_mid = sys.argv[1]
output_mid = sys.argv[2]


print("讀取 Vocal MIDI...")

midi = converter.parse(input_mid)


notes = []

for n in midi.flatten().notes:

    if not isinstance(n, note.Note):
        continue

    # 去低音
    if n.pitch.midi < LOW_NOTE:
        continue

    # 去太短音
    if n.duration.quarterLength < MIN_DURATION:
        continue

    notes.append(
        {
            "pitch": n.pitch,
            "offset": float(n.offset),
            "duration": float(n.duration.quarterLength)
        }
    )


print("保留音符:", len(notes))


# ==========================
# 排序
# ==========================

notes.sort(
    key=lambda x: x["offset"]
)


# ==========================
# 合併同音
# ==========================

clean = []


for n in notes:

    if not clean:
        clean.append(n)
        continue


    last = clean[-1]


    same_pitch = (
        n["pitch"] == last["pitch"]
    )

    close = (
        n["offset"]
        <=
        last["offset"]
        +
        last["duration"]
        +
        MERGE_GAP
    )


    if same_pitch and close:

        end1 = (
            last["offset"]
            +
            last["duration"]
        )

        end2 = (
            n["offset"]
            +
            n["duration"]
        )

        last["duration"] = max(
            end1,
            end2
        ) - last["offset"]

    else:

        clean.append(n)



print("合併後:", len(clean))


# ==========================
# 建立新 MIDI
# ==========================

out = stream.Stream()

for n in clean:

    nn = note.Note(
        n["pitch"]
    )

    nn.offset = n["offset"]

    nn.duration.quarterLength = (
        n["duration"]
    )

    out.append(nn)


# 標記樂器名稱
out.insert(
    0,
    "Vocal Melody"
)


print("輸出 MIDI...")

out.write(
    "midi",
    fp=output_mid
)


print(
    "完成:",
    output_mid
)