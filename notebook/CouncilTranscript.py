import json
import re

class CouncilTranscript():
    text = None
    dict = None

    def __init__(self):
        self.text = ""
        self.dict = {
            "info":list(),
            "transcript":list(),
        }
    
    def set_text(self, text):
        self.text = text
    
    def get_simple_text(self):
        lines = []
        for item in self.dict["transcript"]:
            if "speaker" in item:
                lines.append(item["speaker"])
                for utt in item["utt"]:
                    lines.append("({}){}".format(utt["utt_n"], utt["content"]))
            if "action" in item:
                lines.append(item["action"])
        return "\n".join(lines) + "\n"

    def get_utt_by_utt_n(self, utt_n):
        if isinstance(utt_n, list):
            pass
        else:
            utt_n = [utt_n]
        utts = []
        speaker = ""
        for block in self.dict["transcript"]:
            if not "speaker" in block:
                continue
            speaker = block["speaker"]
            for utt in block["utt"]:
                if utt["utt_n"] in utt_n:
                    utts.append({"speaker":speaker, "utt":utt})
        return utts

    def analyze_text(self):
        if self.text == "":
            print("ERROR: no data")
            return

        re_header = re.compile(r"(?P<tag>.+)：(?P<val>.+)")
        re_hline = re.compile(r"[─◇]+")
        re_speaker = re.compile(r"(?P<speaker>○[^）)]+[）)])(　|$)")
        re_action = re.compile(r"[　]*(?P<action>〔.+〕.*)$")
        re_timekeeper = re.compile(r"[　]+(?P<time>(午前|午後).*)$")

        _status = "header"
        idx = 0
        for line in self.text.splitlines():
            line = line.replace("", "")
            # 空行と罫線の行をスキップする
            if line == "" or line == "　":
                continue
            m = re_hline.match(line)
            if m:
                continue
            # "○議事日程"や話者を表す"○話者"が現れたら_statusを変更する
            if line.startswith("○議事日程"):
                _status = "giji_nittei"
                continue
            elif line.startswith("○"):
                _status = "trainscripts"
            # "○議事日程"や話者を表す"○話者"より前のテキストをself.dictに登録する
            if _status == "header":
                m = re_header.match(line)
                if m:
                    self.dict[m.group("tag")] = m.group("val")
                continue
            # "○議事日程"のブロックをself.dict["info"]に登録する
            if _status == "giji_nittei":
                self.dict["info"].append(line)
                continue
            # 以下議事録のメインの記述を解析する
            m = re_action.match(line)
            if m:
                action = m.group("action")
                self.dict["transcript"].append({"action":action})
                continue
            m = re_timekeeper.match(line)
            if m:
                timekeeper = m.group("time")
                self.dict["transcript"].append({"timekeeper":timekeeper.lstrip().replace("　", " ")})
                continue
            m = re_speaker.match(line)
            if m:
                # print("DEBUG:{}".format("re_speaker is True"))
                speaker = m.group("speaker")
                self.dict["transcript"].append({"speaker":speaker.replace("　", " "), "utt":list()})
                line = re_speaker.sub("　", line)
                if line == "　":
                    continue
                self.dict["transcript"][-1]["utt"].append({"utt_n":idx, "content":line.lstrip().replace("　", " ")})
                idx = idx + 1
                continue
            # print("DEBUG: line:{}".format(line))
            self.dict["transcript"][-1]["utt"].append({"utt_n":idx, "content":line.lstrip().replace("　", " ")})
            idx = idx + 1
