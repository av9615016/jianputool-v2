import sys
import xml.etree.ElementTree as ET


def tag(x):
    if "}" in x:
        return x.split("}")[-1]
    return x



def fix(src,dst):


    print("讀取:",src)


    tree=ET.parse(src)

    root=tree.getroot()


    for measure in root.iter():


        if tag(measure.tag)=="measure":


            total=0


            for d in measure.iter():


                if tag(d.tag)=="duration":

                    try:
                        total += float(d.text)
                    except:
                        pass



            # 4/4 divisions=4
            # 一小節=16


            if total > 16:


                print(
                    "修正超長小節:",
                    measure.attrib.get("number"),
                    total
                )


                notes=[]

                for child in list(measure):

                    if tag(child.tag)=="note":

                        notes.append(child)



                # 移除超出的 note

                acc=0


                for n in notes:

                    dur=0

                    for x in n.iter():

                        if tag(x.tag)=="duration":

                            dur=float(x.text)


                    if acc+dur >16:

                        measure.remove(n)

                    else:

                        acc+=dur



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

    fix(
        sys.argv[1],
        sys.argv[2]
    )