from bottle import route, run, get, post, request, template
import bottle
import codecs
import os
import re
import sys
import logging
import openai
from openai import OpenAI
import time
import json
from dotenv import load_dotenv

from CouncilTranscript import CouncilTranscript

def setenv(filename=None):
    if filename is None:
        return
    load_dotenv(os.path.expanduser(filename), override=True, verbose=True)
    openai.api_type = os.getenv("OPENAI_API_TYPE")
    openai.api_base = os.getenv("OPENAI_API_BASE")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_key = os.getenv("OPENAI_API_KEY")

setenv("~/.openai_api_key.sh")
client = OpenAI()
ct = CouncilTranscript()

# _start = time.time()
# response = client.chat.completions.create(
#     model="gpt-3.5-turbo-1106",
#     # model="gpt-4-1106-preview",
#     response_format={"type":"json_object"},
#     messages=[
#         {"role": "system", "content": "type: json_object"},
#         {"role": "user", "content": "こんにちは"},
#     ]
# )
# elapsed_time = time.time() - _start
# print("epapsed_time: {:.3f}s".format(elapsed_time))
# print(response.usage)
# print(response.choices[0].message.content)


bottle.BaseRequest.MEMFILE_MAX = 1048576

@get("/")
def init():
    text = ""
    tsukoku = ""
    summary = ""
    text_utt_n = ""
    return template("index", text=text, tsukoku=tsukoku, summary=summary, text_utt_n=text_utt_n)

@post("/summarize")
def html_index():
    text = request.forms.getunicode("text").replace("\r\n", "\n").rstrip()
    tsukoku = request.forms.getunicode("tsukoku").replace("\r\n", "\n").rstrip()
    if tsukoku == "":
        tsukoku = "(通告はありません)"
    print("INFO: text受信")
    # print("INFO: text={}".format(repr(text)))
    ct.set_text(text)
    ct.analyze_text()
    json_text = json.dumps(ct.dict, ensure_ascii=False) #, indent=2)
    # print("INFO: json_text={}".format(repr(json_text)))
    text_utt_n = ct.get_simple_text().replace(")", ")\t", 1)
    messages=[
        {"role": "system", "content": "入力の議事録はJSON形式です。話者名がspeaker、発話番号がutt_n、発言内容がcontentに記述されています。"},
        {"role": "user", "content": "質問通告と以下の議事録から議員の質問とそれに対する答弁を一問一答の形式でまとめて下さい。質問は具体的に、答弁は簡潔に記述して下さい。質問と答弁には発話番号を[utt_n: X, Y-Z]の書式で付加して下さい。\n質問通告は\n--------\n" + tsukoku + "\n--------\nです。\n議事録:\n" + json_text + "\n"},
        # {"role": "system", "content": (
        #     "入力の議事録はJSON形式です。"
        #     "話者名がspeaker、発話番号がutt_n、発言内容がcontentに記述されています。")},
        # {"role": "user","content": (
        #     "下記の議事録と質問通告から、答弁を一問一答の形式でまとめて下さい。"
        #     "質問は具体的に記述して下さい。質問は\"[問]\"から記述を始めます。"
        #     "答弁は簡潔に記述して下さい。答弁は\"[答]\"から記述を始めます。"
        #     "質問と答弁には発話番号を[utt_n: X, Y-Z]の書式で付加して下さい。\n"
        #     "議事録:\n" + json_text + "\n"
        #     "質問通告:\n" + tsukoku + "\n"
        #     )},
        # {"role": "system", "content": (
        #     "入力の議事録はJSON形式です。"
        #     "話者名がspeaker、発話番号がutt_n、発言内容がcontentに記述されています。")},
        # {"role": "user","content": (
        #     "以下の議事録から議員の質問とそれに対する答弁を一問一答の形式でまとめて下さい。"
        #     "まとめには、その根拠となった発話番号を[utt_n: X, Y-Z]の書式で付加して下さい。"
        #     # "質問は具体的に記述して下さい。" #質問は\"[問]\"から記述を始めます。"
        #     # "答弁は簡潔に記述して下さい。" #答弁は\"[答]\"から記述を始めます。"
        #     # "質問と答弁には、その根拠の発話番号を[utt_n: X, Y-Z]の書式で付加して下さい。\n"
        #     "質問は\"[問][utt_n: X, Y-Z]\"から、答弁は\"[答][utt_n: X, Y-Z]\"から記述を始めます。"
        #     # "通告は、\n--------\n" + tsukoku + "\n--------\nです。\n"
        #     "\n議事録:\n" + json_text + "\n"
        #     )},
    ]
    print("INFO: messages={}".format(repr(messages)))
    print("INFO: clinet.chat.completions.create()開始")
    _start = time.time()
    response = client.chat.completions.create(
        # model="gpt-3.5-turbo-1106",
        model="gpt-4-1106-preview",
        # response_format={"type":"json_object"},
        temperature=0.0,
        max_tokens=4096,  # 4096 is max_tokens of gpt-4-1106-preview
        messages=messages,
    )
    elapsed_time = time.time() - _start
    print("INFO: clinet.chat.completions.create()完了")
    fee = 161.76 * ((response.usage.prompt_tokens / 1000) * 0.01 + (response.usage.completion_tokens / 1000) * 0.03)
    print("INFO: epapsed_time: {:.3f}s".format(elapsed_time))
    print("INFO: fee:{:.1f}円 {}".format(fee, response.usage))
    # print("INFO: {}".format(response.choices[0].message.content))
    summary = response.choices[0].message.content
    return template("index", text=text, tsukoku=tsukoku, summary=summary, text_utt_n=text_utt_n)

@post("/make_topics")
def html_index():
    text = request.forms.getunicode("text").replace("\r\n", "\n").rstrip()
    tsukoku = request.forms.getunicode("tsukoku").replace("\r\n", "\n").rstrip()
    summary = request.forms.getunicode("summary").replace("\r\n", "\n").rstrip()
    if tsukoku == "":
        tsukoku = "(通告はありません)"
    ct.set_text(text)
    ct.analyze_text()
    json_text = json.dumps(ct.dict, ensure_ascii=False) #, indent=2)
    text_utt_n = ct.get_simple_text().replace(")", ")\t", 1)
    messages=[
        {"role": "system", "content": (
            "入力の議事録はJSON形式です。"
            "話者名がspeaker、発話番号がutt_n、発言内容がcontentに記述されています。"
            )},
        {"role": "user","content": (
            "議事録から、次の書式で話題を箇条書きにして下さい。"
            "\n"
            "1. XXXX\n"
            "2. YYYY\n"
            "\n"
            "\n質問通告:\n" + tsukoku.strip() + "\n"
            "\n議事録:\n" + json_text.strip() + "\n"
            )},
    ]
    print("INFO: messages={}".format(repr(messages)))
    print("INFO: clinet.chat.completions.create()開始")
    _start = time.time()
    response = client.chat.completions.create(
        # model="gpt-3.5-turbo-1106",
        model="gpt-4-1106-preview",
        # response_format={"type":"json_object"},
        temperature=0.0,
        max_tokens=4096,  # 4096 is max_tokens of gpt-4-1106-preview
        messages=messages,
    )
    elapsed_time = time.time() - _start
    print("INFO: clinet.chat.completions.create()完了")
    fee = 161.76 * ((response.usage.prompt_tokens / 1000) * 0.01 + (response.usage.completion_tokens / 1000) * 0.03)
    print("INFO: epapsed_time: {:.3f}s".format(elapsed_time))
    print("INFO: fee:{:.1f}円 {}".format(fee, response.usage))
    # print("INFO: {}".format(response.choices[0].message.content))
    tsukoku = response.choices[0].message.content
    return template("index", text=text, tsukoku=tsukoku, summary=summary, text_utt_n=text_utt_n)

if __name__ == "__main__":
    port = 80
    if len(sys.argv) >= 2:
        port = sys.argv[1]
    run(host="0.0.0.0", port=port, debug=True, reloader=True)
