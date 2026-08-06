# ============================================================
# Jianpu Safe Fix MVP 2.3
#
# MusicXML Safety Repair
#
# raw.musicxml
#       |
#       v
# fixed.musicxml
#
# ============================================================


import sys
from lxml import etree


# ============================================================
# Namespace
# ============================================================

def remove_namespace(tag):

    # 修正 lxml special node
    if not isinstance(tag, str):
        return ""

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag



# ============================================================
# Find divisions
# ============================================================

def get_divisions(root):

    for e in root.iter():

        tag = remove_namespace(
            e.tag
        )

        if tag == "divisions":

            try:
                return int(e.text)

            except:
                pass


    return 480



# ============================================================
# Safe integer
# ============================================================

def safe_int(value):

    try:
        return int(value)

    except:
        return 0



# ============================================================
# Fix duration
# ============================================================

def fix_duration(root, divisions):


    count = 0


    for e in root.iter():


        tag = remove_namespace(
            e.tag
        )


        if tag == "duration":


            value = safe_int(
                e.text
            )


            if value <= 0:

                e.text = "1"

                count += 1



    print(
        "修正 duration:",
        count
    )



# ============================================================
# Fix rests
# ============================================================

def fix_rests(root):


    count = 0


    for note in root.iter():


        if remove_namespace(note.tag) != "note":
            continue


        has_pitch = False

        has_rest = False


        for child in note:


            tag = remove_namespace(
                child.tag
            )


            if tag == "pitch":

                has_pitch = True


            if tag == "rest":

                has_rest = True



        # note 沒 pitch 也沒 rest

        if not has_pitch and not has_rest:


            rest = etree.Element(
                "rest"
            )


            note.insert(
                0,
                rest
            )


            count += 1



    print(
        "修正空白 note:",
        count
    )



# ============================================================
# Remove invalid nodes
# ============================================================

def clean_nodes(root):


    remove = []


    for e in root.iter():


        if not isinstance(
            e.tag,
            str
        ):

            remove.append(
                e
            )


    for e in remove:


        parent = e.getparent()


        if parent is not None:

            parent.remove(
                e
            )


    print(
        "移除特殊 XML node:",
        len(remove)
    )



# ============================================================
# Main
# ============================================================

def main():


    if len(sys.argv) < 3:


        print(
            "使用:"
        )

        print(
            "python jianpu_safe_fix.py input.musicxml output.musicxml"
        )

        return



    input_file = sys.argv[1]

    output_file = sys.argv[2]



    print("="*50)

    print(
        "Jianpu Safe Fix MVP 2.3"
    )

    print("="*50)



    print(
        "讀取:",
        input_file
    )



    parser = etree.XMLParser(
        remove_comments=False,
        recover=True
    )


    tree = etree.parse(
        input_file,
        parser
    )


    root = tree.getroot()



    # 清理特殊節點

    clean_nodes(
        root
    )



    divisions = get_divisions(
        root
    )


    print(
        "Divisions:",
        divisions
    )



    fix_duration(
        root,
        divisions
    )


    fix_rests(
        root
    )



    tree.write(
        output_file,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )



    print(
        "完成:"
    )

    print(
        output_file
    )



if __name__ == "__main__":

    main()