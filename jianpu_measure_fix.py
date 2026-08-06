# ============================================================
# jianpu_measure_fix.py
#
# JianpuTool Professional MVP 2.3.2
#
# MusicXML Measure Fix
#
# Fix:
#   - empty measure
#   - invalid measure duration
#   - jianpu_ly KeyError
#
# ============================================================


import sys
from lxml import etree



# ------------------------------------------------------------
# namespace
# ------------------------------------------------------------

def tag(x):

    if "}" in x:
        return x.split("}",1)[1]

    return x



# ------------------------------------------------------------
# calculate duration
# ------------------------------------------------------------

def get_duration(measure):

    total=0


    for note in measure.iter():

        if tag(note.tag)=="note":


            for child in note:

                if tag(child.tag)=="duration":

                    try:

                        total += int(child.text)

                    except:

                        pass


    return total



# ------------------------------------------------------------
# get divisions
# ------------------------------------------------------------

def get_divisions(root):

    for e in root.iter():

        if tag(e.tag)=="divisions":

            try:

                return int(e.text)

            except:

                pass


    return 1



# ------------------------------------------------------------
# remove empty measures
# ------------------------------------------------------------

def remove_empty_measure(root):


    remove=[]


    for parent in root.iter():

        for child in list(parent):


            if tag(child.tag)=="measure":


                has_note=False


                for n in child.iter():

                    if tag(n.tag)=="note":

                        has_note=True



                if not has_note:

                    remove.append(
                        (parent,child)
                    )



    for p,c in remove:

        p.remove(c)



    print(
        "移除空小節:",
        len(remove)
    )



# ------------------------------------------------------------
# normalize measure
# ------------------------------------------------------------

def fix_measure(root):


    divisions=get_divisions(root)


    print(
        "Divisions:",
        divisions
    )


    max_tick = divisions * 4



    count=0


    for measure in root.iter():


        if tag(measure.tag)!="measure":

            continue



        dur=get_duration(
            measure
        )


        # -----------------------------------
        # 移除沒有內容的小節
        # -----------------------------------

        if dur==0:

            continue



        # -----------------------------------
        # 過長小節保護
        # -----------------------------------

        if dur > max_tick:


            print(
                "修正超長小節:",
                measure.get("number"),
                dur
            )


            # 找最後 note
            notes=[]


            for n in measure.iter():

                if tag(n.tag)=="note":

                    notes.append(n)



            if notes:


                last=notes[-1]


                for c in list(last):

                    if tag(c.tag)=="duration":

                        old=int(c.text)


                        new=max(
                            1,
                            max_tick-(dur-old)
                        )


                        c.text=str(new)


                        break



        count+=1



    print(
        "處理小節:",
        count
    )



# ------------------------------------------------------------
# main
# ------------------------------------------------------------

def main():


    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python jianpu_measure_fix.py input.musicxml output.musicxml"
        )

        return



    src=sys.argv[1]

    dst=sys.argv[2]



    print(
        "讀取:",
        src
    )



    parser=etree.XMLParser(
        remove_blank_text=True
    )


    tree=etree.parse(
        src,
        parser
    )


    root=tree.getroot()



    remove_empty_measure(
        root
    )


    fix_measure(
        root
    )



    tree.write(

        dst,

        encoding="UTF-8",

        xml_declaration=True,

        pretty_print=True

    )


    print(
        "完成:",
        dst
    )



if __name__=="__main__":

    main()