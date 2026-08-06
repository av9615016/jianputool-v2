# ============================================================
# jianpu_safe_fix.py
#
# JianpuTool Professional
# MusicXML Final Cleaner
#
# Fix:
# - jianpu_ly KeyError 8.75 / 9.25 / 9.5 / 11.0
# - wrong time signature
# - invalid duration
# ============================================================


import sys
import xml.etree.ElementTree as ET



def clean_tag(tag):

    if "}" in tag:
        return tag.split("}")[-1]

    return tag



def fix_musicxml(input_file, output_file):


    print("=" * 50)
    print("Jianpu Safe Fix FINAL")
    print("=" * 50)


    print(
        "讀取:",
        input_file
    )


    tree = ET.parse(
        input_file
    )

    root = tree.getroot()



    # ----------------------------------------
    # 修正拍號
    # ----------------------------------------

    for elem in root.iter():


        if clean_tag(elem.tag) == "time":


            for child in elem:


                name = clean_tag(child.tag)


                if name == "beats":

                    child.text = "4"


                elif name == "beat-type":

                    child.text = "4"



    # ----------------------------------------
    # 修正 divisions
    # ----------------------------------------

    for elem in root.iter():

        if clean_tag(elem.tag) == "divisions":

            elem.text = "4"



    # ----------------------------------------
    # 移除錯誤 measure 屬性
    # ----------------------------------------

    for elem in root.iter():


        if clean_tag(elem.tag) == "measure":


            if "implicit" in elem.attrib:

                del elem.attrib["implicit"]



    # ----------------------------------------
    # 修正 duration
    # ----------------------------------------

    for elem in root.iter():


        if clean_tag(elem.tag) == "duration":


            try:

                value = float(elem.text)


                if value <= 0:

                    elem.text = "1"


            except:

                elem.text = "1"



    # ----------------------------------------
    # 移除空 note
    # ----------------------------------------

    remove_list=[]


    for parent in root.iter():


        for child in list(parent):


            if clean_tag(child.tag)=="note":


                has_pitch=False
                has_rest=False


                for n in child:


                    t=clean_tag(n.tag)


                    if t=="pitch":

                        has_pitch=True


                    if t=="rest":

                        has_rest=True



                if not has_pitch and not has_rest:

                    remove_list.append(
                        (parent,child)
                    )



    for parent,child in remove_list:

        parent.remove(child)



    print(
        "移除空 note:",
        len(remove_list)
    )



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "完成:",
        output_file
    )



# ============================================================
# main
# ============================================================

if __name__=="__main__":


    if len(sys.argv)<3:


        print(
            "python jianpu_safe_fix.py input.musicxml output.musicxml"
        )

        exit()



    fix_musicxml(

        sys.argv[1],

        sys.argv[2]

    )