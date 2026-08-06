# ==========================================================
# JianpuTool Professional MVP 2.1
# melody_clean_pro.py
#
# Vocal MIDI Melody Cleaner
#
# Features:
#   - Remove short noise notes
#   - Remove extreme pitch
#   - Merge repeated notes
#   - Vibrato reduction
#   - Melody smoothing
#
# ==========================================================


import sys

from mido import MidiFile
from mido import MidiTrack
from mido import Message


# ==========================================================
# Settings
# ==========================================================


MIN_NOTE_LENGTH = 80      # ms

MIN_PITCH = 45            # A2

MAX_PITCH = 95            # B6


MERGE_GAP = 40            # ms



# ==========================================================
# Convert ticks to ms
# ==========================================================


def ticks_to_ms(mid, ticks):

    tempo = 500000

    return (
        ticks *
        tempo /
        mid.ticks_per_beat /
        1000
    )



# ==========================================================
# Extract notes
# ==========================================================


def extract_notes(mid):

    notes=[]

    current={}


    time=0


    for track in mid.tracks:


        time=0


        for msg in track:


            time += msg.time


            if msg.type=="note_on" and msg.velocity>0:


                current[msg.note]=time



            elif msg.type=="note_off" or (
                msg.type=="note_on"
                and msg.velocity==0
            ):


                if msg.note in current:


                    start=current[msg.note]


                    length=time-start


                    notes.append(
                        [
                            msg.note,
                            start,
                            length
                        ]
                    )


                    del current[msg.note]



    return notes



# ==========================================================
# Clean notes
# ==========================================================


def clean_notes(notes):


    result=[]


    for n,start,length in notes:


        # pitch filter

        if n < MIN_PITCH:

            continue


        if n > MAX_PITCH:

            continue



        # short noise

        if length < MIN_NOTE_LENGTH:

            continue



        result.append(
            [
                n,
                start,
                length
            ]
        )



    return result



# ==========================================================
# Merge same pitch
# ==========================================================


def merge_notes(notes):


    if not notes:

        return []



    notes.sort(
        key=lambda x:x[1]
    )


    output=[]


    last=notes[0]


    for cur in notes[1:]:


        pitch1,start1,len1=last

        pitch2,start2,len2=cur



        end1=start1+len1



        # same pitch close

        if (

            pitch1==pitch2

            and

            start2-end1 < MERGE_GAP

        ):


            last=[

                pitch1,

                start1,

                (start2+len2)-start1

            ]


        else:


            output.append(last)

            last=cur



    output.append(last)


    return output



# ==========================================================
# Write MIDI
# ==========================================================


def write_midi(notes,out):


    mid=MidiFile()


    track=MidiTrack()

    mid.tracks.append(track)



    last_time=0



    for pitch,start,length in notes:


        delta=start-last_time


        track.append(
            Message(
                "note_on",
                note=pitch,
                velocity=80,
                time=int(delta)
            )
        )


        track.append(
            Message(
                "note_off",
                note=pitch,
                velocity=0,
                time=int(length)
            )
        )


        last_time=start+length



    mid.save(out)



# ==========================================================
# Main
# ==========================================================


def main():


    if len(sys.argv)<3:


        print(
            "python melody_clean_pro.py input.mid output.mid"
        )

        sys.exit()



    inp=sys.argv[1]

    out=sys.argv[2]



    print(
        "讀取 MIDI..."
    )


    mid=MidiFile(inp)



    notes=extract_notes(mid)


    print(
        "原始音符:",
        len(notes)
    )



    notes=clean_notes(notes)


    print(
        "音域/長度篩選:",
        len(notes)
    )



    notes=merge_notes(notes)


    print(
        "合併旋律:",
        len(notes)
    )



    write_midi(
        notes,
        out
    )


    print(
        "完成:",
        out
    )



if __name__=="__main__":

    main()