"""
Script that holds functions to parse xml - used in api query
"""

#packages

import xml.etree.ElementTree as ET

#Parser Functions
def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _text(el):
    return "".join(el.itertext()).strip()


def _parse_persons(root):
    person_map = {}
    for person in root.findall(".//{*}TLCPerson"):
        eid = person.get("eId")
        show_as = person.get("showAs")
        if eid and show_as:
            person_map[eid] = show_as
    return person_map


def _resolve_speaker(by_attr, person_map, fallback_text=None):
    if by_attr:
        eid = by_attr.lstrip("#")
        if eid in person_map:
            return person_map[eid]
    return fallback_text


def _parse_speech(speech_el, person_map):
    from_text = None
    paras = []
    for child in speech_el:
        tag = _local(child.tag)
        if tag == "from":
            from_text = _text(child)
        elif tag == "p":
            paras.append(_text(child))

    speaker = _resolve_speaker(speech_el.get("by"), person_map, fallback_text=from_text)
    return speaker, "\n".join(p for p in paras if p)


def _walk_section(section_el, inherited_title, contributions_list, person_map):
    heading = None
    for child in section_el:
        tag = _local(child.tag)
        if tag == "heading":
            heading = _text(child)

    section_title = heading or inherited_title

    for child in section_el:
        tag = _local(child.tag)

        if tag == "speech":
            speaker, text = _parse_speech(child, person_map)
            if text:
                contributions_list.append({
                    "text_type": "speech",
                    "speaker": speaker,
                    "text": text,
                    "section_title": section_title,
                })

        elif tag == "summary":
            text = _text(child)
            if text:
                contributions_list.append({
                    "text_type": "summary",
                    "speaker": None,
                    "text": text,
                    "section_title": section_title,
                })

        elif tag == "answer":
            text = _text(child)
            if text:
                speaker = _resolve_speaker(child.get("by"), person_map)
                contributions_list.append({
                    "text_type": "speech",
                    "speaker": speaker,
                    "text": text,
                    "section_title": section_title,
                })

        elif tag == "debateSection":
            _walk_section(child, section_title, contributions_list, person_map)


def parse_debate_xml(xml_bytes):
    root = ET.fromstring(xml_bytes)
    body = root.find(".//{*}debateBody")

    debates = {}
    if body is None:
        return debates

    person_map = _parse_persons(root)

    for section in body.findall("{*}debateSection"):
        heading = None
        for child in section:
            if _local(child.tag) == "heading":
                heading = _text(child)
                break

        title = heading or section.get("name", "Untitled")
        contributions_list = debates.setdefault(title, [])
        _walk_section(section, title, contributions_list, person_map)

    return debates