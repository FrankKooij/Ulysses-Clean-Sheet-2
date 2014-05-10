# python3.3
# clean_sheet.py
# 2014-05-10 at 18:52

# MIT (c) 2014 RoyRogers56

## Clean blank lines in Ulysses sheets:
# One blank line after each paragraph, except lists, quotes and code;
# Strips blank line after heading 3-6
# Strips double spaces.

## RegEx find & replace:
# Add two lines at top of sheet in UL codeblock:
# '' find: regex-pattern
# '' repl: repl-pattern
# See: https://docs.python.org/3.3/howto/regex.html
# Attributes (in link, image, and video) and Attachments are left untouched

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


use_regex = False
re_from = ""
re_to = ""


def regex_parse_par(p):
    global use_regex

    try:
        for elem in p.iter():
            if elem.tag == "p":
                if elem.text:
                    elem.text = re.sub(re_from, re_to, elem.text)
            elif elem.tag == "tag":
                continue
            elif elem.tag in ("tags", "attribute"):
                if elem.tail:
                    elem.tail = re.sub(re_from, re_to, elem.tail)
            else:
                if elem.text:
                    elem.text = re.sub(re_from, re_to, elem.text)
                if elem.tail:
                    elem.tail = re.sub(re_from, re_to, elem.tail)
        return ET.tostring(p, "unicode", "xml")
    except Exception as e:
        use_regex = False
        print(e)
        msg = '<p><tags><tag kind="comment">%% </tag></tags>Error in RegEx: '\
              + '<element kind="code" startTag="`">"' + re_from + '", "' + re_to + '" : ' + str(e)\
              + '</element></p>\n'
        return msg + ET.tostring(p, "unicode", "xml")


def check_for_regex(par):
    global use_regex
    global re_from
    global re_to

    match = re.search(r'<p><tags><tag kind="codeblock">\'\' </tag></tags>find: (.+)</p>', par)
    if match:
        re_from = match.group(1)
        return True
    match = re.search(r'<p><tags><tag kind="codeblock">\'\' </tag></tags>repl: (.+)</p>', par)
    if match:
        re_to = match.group(1)
        use_regex = True
        print("RegEx from:", re_from)
        print("RegEx to  :", re_to)
        return True

    return False


xml_file = input_file + "/Content.xml"
xml_doc = ET.parse(xml_file)

xml_body = xml_doc.find("string")

xml_txt = '<string xml:space="preserve">'
add_blank = False
next_blank = False
p_num = 0

for p in xml_body.iterfind("p"):
    par = ET.tostring(p, "unicode", "xml")
    p_num += 1
    if p_num < 3 and check_for_regex(par):
        continue

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

    if use_regex:
        xml_txt += regex_parse_par(p)
    else:
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
subprocess.call(['open', input_file])
print("Ulysses file processed:", input_file)
