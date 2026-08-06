# jianpu_final_fix.py

import sys
import xml.etree.ElementTree as ET


def tag(x):

    if "}" in x:
        return x.split("}")[-1]

    return x



def fix(xml_in, xml_out):


    print("讀取:",xml_in)


    tree=ET.parse(
        xml_in
    )

    root=tree.getroot()



    # namespace

    for elem in root.iter():


        if tag(elem.tag)=="time":


            for c in elem:

                if tag(c.tag)=="beats":

                    c.text="4"


                if tag(c.tag)=="beat-type":

                    c.text="4"



    # 修正 measure

    for measure in root.iter():


        if tag(measure.tag)=="measure":


            for attr in list(measure.attrib):

                if attr=="implicit":

                    del measure.attrib[attr]



    tree.write(
        xml_out,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "完成:",
        xml_out
    )



if __name__=="__main__":

    fix(
        sys.argv[1],
        sys.argv[2]
    )