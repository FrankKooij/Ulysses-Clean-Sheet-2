# python3.3
# clean_sheet.py
# 2014-05-10 at 08:56

# MIT (c) 2014 RoyRogers56

# Clean blank lines in Ulysses sheets:
# One blank line after each paragraph, except lists, quotes and code;
# Strips blank line after heading 3-6
# Strips double spaces.

# Use Hazel to trigger script, for smooth laundry service :)

import subprocess
import sys
import xml.etree.ElementTree as ET
import re

input_file = ""

if len(sys.argv) > 1:
    if sys.argv[1] != "":
        input_file = sys.argv[1]

if input_file == "":
    input_file = "test.ulysses"
    # print("*** No input file!")
    # quit()


def write_file(filename, file_content):
    f = open(filename, "w", encoding='utf-8')
    f.write(file_content)
    f.close()


xml_file = input_file + "/Content.xml"
xml_doc = ET.parse(xml_file)

xml_body = xml_doc.find("string")

xml_txt = '<string xml:space="preserve">'
add_blank = False
next_blank = False
for p in xml_body.iterfind("p"):
    par = ET.tostring(p, "unicode", "xml")

    if add_blank:
        xml_txt += "<p />\n"
        add_blank = False

    if par.strip() == "<p />":
        if add_blank:
            xml_txt += "<p />\n"
        add_blank = False
        continue

    if '<tag kind="orderedList">' in par \
            or '<tag kind="unorderedList">' in par \
            or '<tag kind="codeblock">' in par \
            or '<tag kind="blockquote">' in par \
            or '<tag kind="comment">' in par:
        # No blank line after list par and blockquote, except last.
        add_blank = False
        next_blank = True
    elif '<tag kind="heading1' in par or '<tag kind="heading2' in par:
        # Blank line after heading1-2
        if next_blank:
            xml_txt += "<p />\n"
            next_blank = False
        add_blank = True
    elif '<tag kind="heading' in par:
        # No blank line after heading3-6
        if next_blank:
            xml_txt += "<p />\n"
            next_blank = False
        add_blank = False
    else:
        if next_blank:
            xml_txt += "<p />\n"
            next_blank = False
        add_blank = True

    xml_txt += par

xml_txt = xml_txt + '</string>\n'

# Clean double spaces:
xml_txt = re.sub(r" +", r" ", xml_txt)

# write_file("debug_body.xml", xml_txt)

xml_body.clear()
xml_body.set("xml:space", "preserve")
for p in ET.XML(xml_txt).iterfind("p"):
    xml_body.append(p)

xml_doc.write("debug.xml")

xml_doc.write(xml_file)
print("Ulysses file processed:", input_file)

subprocess.call(['open', input_file])
