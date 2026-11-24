import hashlib
import json
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent
TARGET = Path("D:/Users/Personal/Homework/云计算ppt2026/简答题.docx")
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def read_document(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, "ZIP integrity check failed"
        root = ET.fromstring(archive.read("word/document.xml"))
        blocks = root.findall("./w:body/w:p", NS)
        texts = ["".join(t.text or "" for t in block.findall(".//w:t", NS)) for block in blocks]
        rels = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        relmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
        pictures = {}
        for index, block in enumerate(blocks):
            blips = block.findall(".//a:blip", NS)
            if blips:
                values = []
                for blip in blips:
                    rid = blip.attrib["{" + NS["r"] + "}embed"]
                    media_path = posixpath.normpath("word/" + relmap[rid])
                    values.append(hashlib.sha256(archive.read(media_path)).hexdigest())
                pictures[index] = values
        return texts, pictures


def normalized(text):
    return re.sub(r"\s+", "", text)


original, _ = read_document(ROOT / "original.docx")
actual, pictures = read_document(TARGET)
source = json.loads((ROOT / "all-chapters.json").read_text(encoding="utf-8"))
assert len(actual) == 312, f"Unexpected document block count: {len(actual)}"
assert source["totalQuestions"] == 41
mapping = {}
cursor = 0
for baseline_index, text in enumerate(original):
    while cursor < len(actual) and actual[cursor] != text:
        cursor += 1
    assert cursor < len(actual), f"Missing or changed original block: {text}"
    mapping[baseline_index] = cursor
    cursor += 1

question_indexes = []
label_indexes = []
text_answers = 0
image_answers = 0
empty_answers = []
chapter_results = []
baseline_chapter = 0
baseline_questions = []
for index, text in enumerate(original):
    if re.match(r"^第[一二三四五六七八九十]+章 ", text):
        baseline_chapter += 1
        assert text == source["chapters"][baseline_chapter - 1]["title"]
    elif re.match(r"^\d+\. ", text):
        baseline_questions.append((baseline_chapter, index, text))
assert len(baseline_questions) == 41

for chapter_num, baseline_index, question_text in baseline_questions:
    number = int(question_text.split(".", 1)[0])
    chapter = source["chapters"][chapter_num - 1]
    question = chapter["questions"][number - 1]
    stem = re.sub(r"^\d+\.\s*\(简答题\)\s*", "", question["stem"])
    assert normalized(stem) == normalized(question_text.split(". ", 1)[1]), f"Question mismatch: {chapter_num}-{number}"
    start = mapping[baseline_index]
    end = mapping[baseline_index + 1] if baseline_index + 1 < len(original) else len(actual)
    segment = actual[start + 1:end]
    assert segment and segment[0].startswith("我的答案"), f"Missing answer label: {chapter_num}-{number}"
    question_indexes.append(start)
    label_indexes.append(start + 1)
    image_blocks = [i for i in range(start + 1, end) if i in pictures]
    if question["images"]:
        assert len(image_blocks) == len(question["images"]), f"Image count mismatch: {chapter_num}-{number}"
        for j, (image, block_index) in enumerate(zip(question["images"], image_blocks), 1):
            ext = Path(image["src"]).suffix
            local = ROOT / f"answer-{chapter_num:02d}-{number:02d}-{j}{ext}"
            digest = hashlib.sha256(local.read_bytes()).hexdigest()
            assert pictures[block_index] == [digest], f"Image changed: {chapter_num}-{number}"
        image_answers += 1
    elif question["answerText"].strip():
        assert not image_blocks, f"Unexpected answer image: {chapter_num}-{number}"
        answer_text = "".join(segment[1:])
        assert normalized(answer_text) == normalized(question["answerText"]), f"Answer text mismatch: {chapter_num}-{number}"
        text_answers += 1
    else:
        assert segment == ["我的答案：未读取到已保存答案（本题暂未补入）。"], f"Empty answer not marked: {chapter_num}-{number}"
        empty_answers.append([chapter_num, number])

assert text_answers == 32 and image_answers == 6
assert empty_answers == [[3, 3], [3, 4], [3, 5]]
assert len(pictures) == 6
original_indexes = set(mapping.values())
added_text_indexes = [i for i in range(len(actual)) if i not in original_indexes and i not in pictures]
for chapter in source["chapters"]:
    chapter_results.append({"chapter": chapter["chapter"], "title": chapter["title"], "questions": len(chapter["questions"]), "answers": sum(bool(q["answerText"].strip() or q["images"]) for q in chapter["questions"])})
print(json.dumps({
    "checkedFile": str(TARGET),
    "blocks": len(actual),
    "questionCount": len(question_indexes),
    "textAnswers": text_answers,
    "imageAnswers": image_answers,
    "emptyAnswers": empty_answers,
    "originalContentPreserved": True,
    "allAnswerTextsMatchSources": True,
    "allImageHashesMatchSources": True,
    "chapters": chapter_results,
    "questionIndexes": question_indexes,
    "labelIndexes": label_indexes,
    "addedTextIndexes": added_text_indexes,
    "imageIndexes": list(pictures),
}, ensure_ascii=False, indent=2))
