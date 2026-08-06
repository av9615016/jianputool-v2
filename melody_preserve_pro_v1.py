# ============================================================
# melody_preserve_pro_v1.py
#
# JianpuTool Professional
#
# Vocal MIDI Preserve Mode
#
# 目的:
# 保留流行歌曲人聲旋律
#
# ============================================================


import sys
from mido import MidiFile, MidiTrack, Message



# ============================================================
# Read MIDI
# ============================================================

def read_notes(path):

    print("讀取 Vocal MIDI...")


    mid = MidiFile(path)


    notes=[]


    active={}


    for track in mid.tracks:


        tick=0


        for msg in track:


            tick += msg.time



            if msg.type=="note_on" and msg.velocity>0:


                active[msg.note]=tick



            elif (
                msg.type=="note_off"
                or
                (
                    msg.type=="note_on"
                    and msg.velocity==0
                )
            ):


                if msg.note in active:


                    start=active.pop(
                        msg.note
                    )


                    notes.append(
                        {
                            "pitch":msg.note,
                            "start":start,
                            "end":tick
                        }
                    )


    print(
        "原始音符:",
        len(notes)
    )


    return notes



# ============================================================
# Vocal Range Preserve
# ============================================================

def preserve_filter(notes):


    print(
        "Vocal Preserve Mode..."
    )


    result=[]


    for n in notes:


        pitch=n["pitch"]

        length=n["end"]-n["start"]



        # 放寬人聲範圍

        if pitch < 28:
            continue


        if pitch > 105:
            continue



        # 只刪真正雜訊

        if length <= 2:
            continue



        result.append(
            n
        )


    print(
        "保留音符:",
        len(result)
    )


    return result



# ============================================================
# Remove Duplicate Overlap
# ============================================================

def remove_overlap(notes):


    print(
        "整理重疊音..."
    )


    notes.sort(
        key=lambda x:
        (
            x["start"],
            x["pitch"]
        )
    )


    result=[]


    last={}


    for n in notes:


        key=n["pitch"]


        if key in last:


            old=last[key]


            # 太接近視為同一音

            if abs(
                n["start"]
                -
                old["start"]
            ) < 15:


                if n["end"] > old["end"]:

                    old["end"]=n["end"]


                continue



        result.append(n)

        last[key]=n



    print(
        "整理後:",
        len(result)
    )


    return result



# ============================================================
# Write MIDI Safe
# ============================================================

def write_midi(notes,out):


    print(
        "輸出 MIDI..."
    )


    mid=MidiFile(
        ticks_per_beat=480
    )


    track=MidiTrack()

    mid.tracks.append(track)



    notes.sort(
        key=lambda x:
        (
            x["start"],
            x["pitch"]
        )
    )



    current=0



    for n in notes:


        start=max(
            0,
            int(n["start"])
        )


        end=max(
            start+1,
            int(n["end"])
        )


        delta=start-current


        if delta<0:

            delta=0



        track.append(
            Message(
                "note_on",
                note=int(n["pitch"]),
                velocity=90,
                time=delta
            )
        )


        track.append(
            Message(
                "note_off",
                note=int(n["pitch"]),
                velocity=0,
                time=end-start
            )
        )


        current=end



    mid.save(out)


    print(
        "完成:",
        out
    )



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv)<3:

        print(
            "python melody_preserve_pro_v1.py input.mid output.mid"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]



    notes=read_notes(inp)


    notes=preserve_filter(
        notes
    )


    notes=remove_overlap(
        notes
    )


    write_midi(
        notes,
        out
    )



if __name__=="__main__":

    main()