# ==========================================================
# jianpu_safe_fix.py
#
# JianpuTool Professional MVP 2.2
#
# MusicXML -> Safe MusicXML
#
# Fix:
#   - jianpu_ly barcheck fail
#   - remove tie
#   - normalize duration
#   - measure protection
#
# ==========================================================


import sys
from lxml import etree
from fractions import Fraction


DIVISION_DEFAULT = 4



def remove_namespace(tag):
    if "}" in tag:
        return tag.split("}")[1]
    return tag



def get_divisions(root):

    for e in root.iter():
        if remove_namespace(e.tag) == "divisions":
            return int(e.text)

    return DIVISION_DEFAULT



def remove_ties(root):

    count = 0

    for tie in root.xpath(
        "//*[local-name()='tie']"
    ):
        parent = tie.getparent()

        if parent is not None:
            parent.remove(tie)
            count += 1


    for tied in root.xpath(
        "//*[local-name()='tied']"
    ):
        parent = tied.getparent()

        if parent is not None:
            parent.remove(tied)
            count += 1


    return count




def fix_duration(root, divisions):

    fixed = 0


    # 四分音符最大4拍
    max_duration = divisions * 4


    for duration in root.xpath(
        "//*[local-name()='duration']"
    ):

        try:

            value = int(duration.text)


            if value > max_duration:

                duration.text = str(
                    max_duration
                )

                fixed += 1


        except:

            pass


    return fixed





def check_measure(root, divisions):

    measures = 0
    errors = 0


    for measure in root.xpath(
        "//*[local-name()='measure']"
    ):

        measures += 1


        total = 0


        for duration in measure.xpath(
            ".//*[local-name()='duration']"
        ):

            try:
                total += int(duration.text)

            except:
                pass


        beats = total / divisions


        # 允許誤差
        if beats > 4.1:

            errors += 1


    return measures, errors





def fix_voice(root):

    """
    移除 voice 造成的
    jianpu_ly 排版問題
    """

    count = 0


    for voice in root.xpath(
        "//*[local-name()='voice']"
    ):

        parent = voice.getparent()

        if parent is not None:

            parent.remove(voice)

            count += 1


    return count





def main():


    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python jianpu_safe_fix.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    input_file=sys.argv[1]

    output_file=sys.argv[2]


    print("="*50)

    print(
        "Jianpu Safe Fix MVP 2.2"
    )

    print("="*50)



    print(
        "讀取:",
        input_file
    )


    parser=etree.XMLParser(
        remove_blank_text=True
    )


    tree=etree.parse(
        input_file,
        parser
    )


    root=tree.getroot()



    divisions=get_divisions(
        root
    )


    print(
        "Divisions:",
        divisions
    )



    print(
        "\n移除 tie..."
    )


    tie_count=remove_ties(
        root
    )


    print(
        "Tie:",
        tie_count
    )



    print(
        "\n修正 duration..."
    )


    duration_count=fix_duration(
        root,
        divisions
    )


    print(
        "Duration:",
        duration_count
    )



    print(
        "\n移除 voice..."
    )


    voice_count=fix_voice(
        root
    )


    print(
        "Voice:",
        voice_count
    )



    measures,errors=check_measure(
        root,
        divisions
    )


    print()

    print(
        "Measures:",
        measures
    )


    print(
        "Measure errors:",
        errors
    )



    tree.write(
        output_file,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )


    print()

    print(
        "完成:"
    )

    print(
        output_file
    )

    print("="*50)




if __name__=="__main__":

    main()