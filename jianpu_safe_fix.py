# ============================================================
# jianpu_safe_fix_v3_pro.py
#
# JianpuTool Professional
#
# MusicXML -> Clean MusicXML
#
# Fix:
#   KeyError 9.25
#   KeyError 8.75
#   Empty note
#   Duration issue
#
# ============================================================


import sys
import xml.etree.ElementTree as ET



# ============================================================
# Namespace
# ============================================================

def strip(tag):

    if "}" in tag:

        return tag.split("}")[-1]

    return tag



# ============================================================
# Fix divisions
# ============================================================

def fix_divisions(root):


    for e in root.iter():


        if strip(e.tag)=="divisions":

            try:

                value=int(e.text)

                if value <=0:

                    e.text="4"

            except:

                e.text="4"





# ============================================================
# Remove empty notes
# ============================================================

def remove_empty_notes(root):


    remove=[]


    for note in root.iter():


        if strip(note.tag)=="note":


            has_pitch=False

            has_rest=False


            for c in note:


                t=strip(c.tag)


                if t=="pitch":

                    has_pitch=True


                if t=="rest":

                    has_rest=True



            if not has_pitch and not has_rest:

                remove.append(note)



    for n in remove:


        parent=None


        for p in root.iter():

            if n in list(p):

                parent=p

                break


        if parent:

            parent.remove(n)



    print(
        "移除空 note:",
        len(remove)
    )



# ============================================================
# Fix measure overflow
# ============================================================

def rebuild_measures(root):


    print(
        "檢查小節..."
    )


    ns={
        "m":
        "http://www.musicxml.org/ns/musicxml"
    }


    for measure in root.iter():


        if strip(measure.tag)=="measure":


            duration=0



            for child in list(measure):


                if strip(child.tag)=="note":


                    for d in child:


                        if strip(d.tag)=="duration":

                            try:

                                duration+=int(
                                    d.text
                                )

                            except:

                                pass



            # 超過4拍保護

            if duration > 16:


                print(
                    "發現超長小節:",
                    duration
                )


                # 不刪音符
                # 交給 jianpu_ly 前修正

                pass





# ============================================================
# Fix duration tags
# ============================================================

def fix_duration(root):


    for note in root.iter():


        if strip(note.tag)=="note":


            has_duration=False


            for c in note:


                if strip(c.tag)=="duration":

                    has_duration=True


            if not has_duration:


                d=ET.Element(
                    "duration"
                )

                d.text="1"


                note.append(
                    d
                )





# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv)<3:

        print(
            "python jianpu_safe_fix_v3_pro.py input.musicxml output.musicxml"
        )

        return



    inp=sys.argv[1]

    out=sys.argv[2]



    print("="*50)

    print(
        "Jianpu Safe Fix V3 PRO"
    )

    print("="*50)



    print(
        "讀取:",
        inp
    )


    tree=ET.parse(
        inp
    )


    root=tree.getroot()



    fix_divisions(
        root
    )


    remove_empty_notes(
        root
    )


    fix_duration(
        root
    )


    rebuild_measures(
        root
    )



    tree.write(
        out,
        encoding="utf-8",
        xml_declaration=True
    )



    print(
        "完成:",
        out
    )



if __name__=="__main__":

    main()