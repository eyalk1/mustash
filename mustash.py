#!/usr/bin/python3
import json
import os
import pdb
from playsound import playsound

REC_FILENAME = "recs.json"
PROMPT = ">>> "
TEMPI = ["fast", "mid", "slow"]


def get_name():
    return input(">>> name - ")


def get_tempo():
    return get_from_options("tempo", ["slow", "midium", "fast"])


def get_files_from_curdir(filetype: str, pred):
    files = list(
        filter(
            lambda filename: filename != "mustash.py"
            and filename != REC_FILENAME
            and os.path.isfile(filename)
            and pred(filename),
            os.listdir(),
        )
    )
    return get_from_options(filetype, files)


def get_chords():
    return get_until_empty("chords")


def get_feels():
    return get_until_empty("feels")


def get_time_signature():
    return get_until_empty("time signature")

def add_new_composition(rec_file):
    name = get_name()
    tempo = get_tempo()
    audio_file = get_files_from_curdir(
        "audio_file",
        lambda filename: filename
        not in [s["audio_file"] for s in rec_file],
    )
    score_file = get_files_from_curdir(
        "score_file",
        lambda filename: filename
        not in [s["score_file"] for s in rec_file],
    )
    chords = get_chords()
    has_line = (
        True
        if get_from_options("has line", ["yes", "no"]) == "yes"
        else False
    )
    feel = get_feels()
    composer = get_from_options(
        "composer", [rec["composer"] for rec in rec_file], add_new=True
    )
    used = input(">>> used - ")
    length = int(input(">>> length - "))
    time_signature = get_time_signature()
    return {
        "name": name,
        "tempo": tempo,
        "audio_file": audio_file,
        "score_file": score_file,
        "chords": chords,
        "has_line": has_line,
        "feel": feel,
        "composer": composer,
        "used": used,
        "length": length,
        "time_signature": time_signature,
    }

def get_recs_names(recs):
    return [r["name"] for r in recs]
    

def main():
    rec_file = json.load(open(REC_FILENAME))

    cmd = ''
    while cmd != "q":
        cmd = input(PROMPT)
        match cmd:
            case "ls":
                print('\n'.join(get_recs_names(rec_file)))
            case "search":
                pass
            case "add":
                rec_file.append(add_new_composition(rec_file))
            case "rm":
                delete = get_from_options("recs", get_recs_names(rec_file))
                rec_file = list(filter(lambda rec:rec["name"] != delete, rec_file))
            case "play":
                play = get_from_options("recs", get_recs_names(rec_file))
                for rec in rec_file:
                    if rec["name"] == play:
                        playsound(rec["audio_file"])
            case "edit":
                pass
            case "q":
                print(rec_file)
                json.dump(rec_file, open(REC_FILENAME, "w"))


def dowhile(action, check, accumulate=False):
    thing = [] if accumulate else None
    while True:
        if accumulate:
            thing.append(action())
        else:
            thing = action()
        if check(thing):
            break
    return thing


def get_from_options(category_name, options, add_new=False):
    if add_new:
        options.append("new")
    prompt_prefix = f">>> {category_name} - "
    optionlist = "\n".join([f"\t{n} - {option}" for n, option in enumerate(options)])
    prompt = f"{prompt_prefix}\n{optionlist}\n{PROMPT}"
    result = dowhile(lambda: int(input(prompt)), lambda answer: answer < len(options))
    if not add_new or result < len(options) - 1:
        return options[result]
    return input(f"enter new {category_name} - ")


def get_until_empty(category):
    return list(filter(
        lambda x: x != "",
        dowhile(
            lambda: input(f"{PROMPT}{category} - "),
            lambda things: things[-1] == "",
            True,
        ),
    ))


if __name__ == "__main__":
    main()
