import sys
import xml.etree.ElementTree as ET


def clean_tag(tag):

    if "}" in tag:
        return tag.split("}")[-1]

    return tag



def fix_musicxml(src,dst):


    print("讀取:",src)


    tree=ET.parse(src)

    root=tree.getroot()



    for elem in root.iter():


        name=clean_tag(elem.tag)



        # =========================
        # 強制 4/4
        # =========================

        if name=="time":


            for c in elem:


                if clean_tag(c.tag)=="beats":

                    c.text="4"


                if clean_tag(c.tag)=="beat-type":

                    c.text="4"



        # =========================
        # divisions
        # =========================

        if name=="divisions":

            elem.text="4"



        # =========================
        # 移除 implicit
        # =========================

        if name=="measure":


            if "implicit" in elem.attrib:

                del elem.attrib["implicit"]



        # =========================
        # duration 保護
        # =========================

        if name=="duration":


            try:

                value=float(elem.text)


                if value<=0:

                    elem.text="1"


            except:

                elem.text="1"



    tree.write(
        dst,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "完成:",
        dst
    )



if __name__=="__main__":


    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )