import mido
import sys


def clean(src,dst):

    mid=mido.MidiFile(src)


    new=mido.MidiFile(
        type=1,
        ticks_per_beat=mid.ticks_per_beat
    )


    track=mido.MidiTrack()

    notes=set()


    for msg in mid.tracks[0]:

        if msg.type=="note_on":

            if msg.note in notes:
                continue

            notes.add(msg.note)


        track.append(msg)


    new.tracks.append(track)

    new.save(dst)



if __name__=="__main__":

    clean(
        sys.argv[1],
        sys.argv[2]
    )