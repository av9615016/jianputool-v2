# ============================================================
# melody_clean_pro.py
#
# JianpuTool Professional MVP 2.3
#
# BasicPitch MIDI
#        |
#        v
# Melody Clean Pro
#        |
#        v
# clean.mid
#
# ============================================================


import sys
from mido import MidiFile, MidiTrack, Message



# ============================================================
# 讀取 MIDI
# ============================================================

def read_notes(mid_file):

    print("讀取 MIDI...")


    mid = MidiFile(mid_file)


    notes = []

    current_time = 0

    active = {}



    for track in mid.tracks:


        time = 0


        for msg in track:


            time += msg.time



            if msg.type == "note_on" and msg.velocity > 0:


                active[msg.note] = time



            elif msg.type in [
                "note_off",
                "note_on"
            ] and msg.velocity == 0:


                if msg.note in active:


                    start = active.pop(
                        msg.note
                    )


                    end = time


                    notes.append(
                        {
                            "pitch": msg.note,
                            "start": start,
                            "end": end
                        }
                    )



    print(
        "原始音符:",
        len(notes)
    )


    return notes



# ============================================================
# 音域 / 長度篩選
# ============================================================

def filter_notes(notes):


    result = []


    for n in notes:


        pitch = n["pitch"]


        duration = (
            n["end"]
            -
            n["start"]
        )


        # 人聲常用範圍

        if pitch < 35:
            continue


        if pitch > 95:
            continue



        # 太短雜音

        if duration < 30:
            continue



        result.append(
            n
        )


    print(
        "音域/長度篩選:",
        len(result)
    )


    return result



# ============================================================
# 相鄰音符合併
# ============================================================

def merge_notes(notes):


    if not notes:
        return []



    notes = sorted(
        notes,
        key=lambda x:x["start"]
    )


    result = []


    last = None



    for n in notes:


        if last is None:

            last = n

            continue



        # 同音且接近

        if (
            n["pitch"] == last["pitch"]
            and
            n["start"] - last["end"] < 50
        ):


            last["end"] = max(
                last["end"],
                n["end"]
            )


        else:


            result.append(
                last
            )

            last = n



    if last:

        result.append(
            last
        )



    print(
        "合併旋律:",
        len(result)
    )


    return result



# ============================================================
# 安全寫 MIDI
# ============================================================

def write_midi(notes, out):


    print(
        "寫入 MIDI..."
    )


    mid = MidiFile(
        ticks_per_beat=480
    )


    track = MidiTrack()

    mid.tracks.append(
        track
    )



    # ★重要：排序

    notes = sorted(
        notes,
        key=lambda x:(
            x["start"],
            x["pitch"]
        )
    )



    current_time = 0



    for n in notes:


        pitch = int(
            n["pitch"]
        )


        start = int(
            max(
                0,
                n["start"]
            )
        )


        end = int(
            max(
                start + 1,
                n["end"]
            )
        )



        delta = start - current_time



        # 防止負時間

        if delta < 0:

            delta = 0



        track.append(
            Message(
                "note_on",
                note=pitch,
                velocity=80,
                time=delta
            )
        )



        track.append(
            Message(
                "note_off",
                note=pitch,
                velocity=0,
                time=end-start
            )
        )


        current_time = end



    mid.save(
        out
    )


    print(
        "完成:",
        out
    )



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv) < 3:

        print(
            "使用:"
        )

        print(
            "python melody_clean_pro.py input.mid output.mid"
        )

        return



    input_mid = sys.argv[1]

    output_mid = sys.argv[2]



    notes = read_notes(
        input_mid
    )


    notes = filter_notes(
        notes
    )


    notes = merge_notes(
        notes
    )


    write_midi(
        notes,
        output_mid
    )



if __name__ == "__main__":

    main()