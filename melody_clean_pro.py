# ============================================================
# melody_clean_pro_v2.4.py
#
# JianpuTool Professional
#
# BasicPitch MIDI
#        |
#        v
# Melody Clean Pro v2.4
#        |
#        v
# clean.mid
#
# 保留旋律版
# ============================================================


import sys
from mido import MidiFile, MidiTrack, Message



# ============================================================
# MIDI Reader
# ============================================================

def read_notes(filename):

    print("讀取 MIDI...")


    mid = MidiFile(filename)


    notes = []

    active = {}


    for track in mid.tracks:


        current = 0


        for msg in track:


            current += msg.time



            if msg.type == "note_on" and msg.velocity > 0:


                active[msg.note] = current



            elif (
                msg.type == "note_off"
                or
                (
                    msg.type == "note_on"
                    and msg.velocity == 0
                )
            ):


                if msg.note in active:


                    start = active.pop(
                        msg.note
                    )


                    end = current


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
# Vocal Range Filter
# ============================================================

def vocal_filter(notes):


    result = []


    for n in notes:


        pitch = n["pitch"]

        length = (
            n["end"]
            -
            n["start"]
        )



        # 放寬人聲範圍

        if pitch < 30:
            continue


        if pitch > 100:
            continue



        # 保留更多短音

        if length < 10:
            continue



        result.append(
            n
        )



    print(
        "音域/長度保留:",
        len(result)
    )


    return result



# ============================================================
# Remove Duplicate Notes
# ============================================================

def remove_duplicate(notes):


    notes = sorted(
        notes,
        key=lambda x:(
            x["start"],
            x["pitch"]
        )
    )


    result=[]


    last=None


    for n in notes:


        if last:


            if (
                n["pitch"]
                ==
                last["pitch"]

                and

                abs(
                    n["start"]
                    -
                    last["start"]
                )
                < 20
            ):


                if n["end"] > last["end"]:

                    last["end"] = n["end"]


                continue



        result.append(
            n
        )


        last=n



    print(
        "去除重複:",
        len(result)
    )


    return result



# ============================================================
# Phrase Merge
# ============================================================

def phrase_merge(notes):


    notes = sorted(
        notes,
        key=lambda x:x["start"]
    )


    result=[]


    last=None


    for n in notes:


        if last is None:

            last=n

            continue



        gap = (
            n["start"]
            -
            last["end"]
        )



        # 同音小間隔合併

        if (
            n["pitch"]
            ==
            last["pitch"]

            and

            gap < 20
        ):


            last["end"] = max(
                last["end"],
                n["end"]
            )


        else:


            result.append(
                last
            )


            last=n



    if last:

        result.append(
            last
        )


    print(
        "Phrase Merge:",
        len(result)
    )


    return result



# ============================================================
# Safe MIDI Writer
# ============================================================

def write_midi(notes, output):


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


    notes = sorted(
        notes,
        key=lambda x:(
            x["start"],
            x["pitch"]
        )
    )


    current = 0



    for n in notes:


        pitch=int(
            n["pitch"]
        )


        start=max(
            0,
            int(n["start"])
        )


        end=max(
            start+1,
            int(n["end"])
        )



        delta=start-current


        if delta < 0:

            delta=0



        track.append(
            Message(
                "note_on",
                note=pitch,
                velocity=90,
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


        current=end



    mid.save(
        output
    )


    print(
        "完成:",
        output
    )



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv)<3:


        print(
            "python melody_clean_pro_v2.4.py input.mid output.mid"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]



    notes=read_notes(
        inp
    )


    notes=vocal_filter(
        notes
    )


    notes=remove_duplicate(
        notes
    )


    notes=phrase_merge(
        notes
    )


    write_midi(
        notes,
        out
    )



if __name__=="__main__":

    main()