# vocal_midi_clean.py
#
# JianpuTool
# Vocal MIDI Cleaner V1.1
#
# BasicPitch Vocal MIDI
#        |
#        v
# Clean Vocal Melody MIDI
#

import sys

from music21 import (
    converter,
    note,
    stream,
    instrument
)


# ==========================
# 設定
# ==========================

LOW_NOTE = 40          # E2 以下移除
MIN_DURATION = 0.08    # 太短音移除
MERGE_GAP = 0.08       # 同音合併距離


# ==========================
# 參數
# ==========================

if len(sys.argv) < 3:
    print(
        "使用方式:\n"
        "python vocal_midi_clean.py input.mid output.mid"
    )
    sys.exit()


input_mid = sys.argv[1]
output_mid = sys.argv[2]


# ==========================
# 讀取 MIDI
# ==========================

print("讀取 Vocal MIDI...")

midi = converter.parse(
    input_mid
)


notes = []


for n in midi.flatten().notes:

    if not isinstance(n, note.Note):
        continue


    # 去除低音
    if n.pitch.midi < LOW_NOTE:
        continue


    # 去除太短音
    if n.duration.quarterLength < MIN_DURATION:
        continue


    notes.append(
        {
            "pitch": n.pitch,
            "offset": float(n.offset),
            "duration": float(
                n.duration.quarterLength
            )
        }
    )


print(
    "保留音符:",
    len(notes)
)


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


    last_end = (
        last["offset"]
        +
        last["duration"]
    )


    close = (
        n["offset"]
        <=
        last_end
        +
        MERGE_GAP
    )


    if same_pitch and close:

        new_end = max(
            last_end,
            n["offset"] + n["duration"]
        )

        last["duration"] = (
            new_end
            -
            last["offset"]
        )

    else:

        clean.append(n)



print(
    "合併後:",
    len(clean)
)


# ==========================
# 建立輸出 MIDI
# ==========================

out = stream.Stream()


# Vocal 樂器標記

vocal_inst = instrument.Instrument()

vocal_inst.instrumentName = (
    "Vocal Melody"
)

out.insert(
    0,
    vocal_inst
)


# 加入音符

for item in clean:

    nn = note.Note(
        item["pitch"]
    )

    nn.offset = (
        item["offset"]
    )

    nn.duration.quarterLength = (
        item["duration"]
    )

    out.append(nn)



# ==========================
# 輸出
# ==========================

print(
    "輸出 MIDI..."
)


out.write(
    "midi",
    fp=output_mid
)


print(
    "完成:",
    output_mid
)