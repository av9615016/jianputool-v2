# fix_jianpu_input.py

import sys
from lxml import etree


src=sys.argv[1]
dst=sys.argv[2]


tree=etree.parse(src)
root=tree.getroot()


# 移除 midi-device
for x in root.xpath(".//midi-device"):
    x.getparent().remove(x)


# 移除 instrument
for x in root.xpath(".//instrument-name"):
    x.text=""


# 保留第一個 part
parts=root.findall(".//part")

if len(parts)>1:
    for p in parts[1:]:
        root.remove(p)


tree.write(
    dst,
    encoding="UTF-8",
    xml_declaration=True
)


print("Jianpu input cleaned")