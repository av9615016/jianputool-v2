# ============================================================
# clean_musicxml.py
#
# JianpuTool MVP 1.1
# CLEAN MUSICXML V34 FIX
#
# Input:
#   raw.musicxml
#
# Output:
#   clean.musicxml
#
# ============================================================


import sys
import os
from lxml import etree


print("================ CLEAN MUSICXML V34 FIX ================")


# ------------------------------------------------------------
# Check arguments
# ------------------------------------------------------------

if len(sys.argv) < 3:

    print(
        "Usage:"
    )

    print(
        "python clean_musicxml.py input.musicxml output.musicxml"
    )

    sys.exit(1)



input_file = sys.argv[1]
output_file = sys.argv[2]



# ------------------------------------------------------------
# Path check
# ------------------------------------------------------------

if not os.path.isfile(input_file):

    raise Exception(
        f"Input MusicXML not found: {input_file}"
    )


if os.path.isdir(output_file):

    raise Exception(
        f"Output path is directory, need file: {output_file}"
    )



# ------------------------------------------------------------
# Load XML
# ------------------------------------------------------------

parser = etree.XMLParser(
    remove_blank_text=True
)


tree = etree.parse(
    input_file,
    parser
)


root = tree.getroot()



# ------------------------------------------------------------
# Remove unnecessary elements
# ------------------------------------------------------------

remove_tags = [

    "encoding",

    "supports",

    "software",

    "creator"

]


for tag in remove_tags:

    for node in root.xpath(
        f".//{tag}"
    ):

        parent = node.getparent()

        if parent is not None:

            parent.remove(node)



# ------------------------------------------------------------
# Fix duration
# ------------------------------------------------------------

for duration in root.xpath(
    ".//duration"
):

    try:

        value = int(
            duration.text
        )


        if value <= 0:

            duration.text = "1"


    except:

        duration.text = "1"



# ------------------------------------------------------------
# Fix divisions
# ------------------------------------------------------------

for divisions in root.xpath(
    ".//divisions"
):

    try:

        value = int(
            divisions.text
        )


        if value <= 0:

            divisions.text = "480"


    except:

        divisions.text = "480"



# ------------------------------------------------------------
# Remove empty lyric
# ------------------------------------------------------------

for lyric in root.xpath(
    ".//lyric"
):

    if len(lyric) == 0:

        parent = lyric.getparent()

        if parent is not None:

            parent.remove(lyric)



# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)



tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True,
    pretty_print=True
)



print(
    "CLEAN MUSICXML DONE:"
)
print(
    output_file
)

print(
    "========================================================"
)