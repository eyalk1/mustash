#!/usr/bin/python3
import json
import os
import pdb
from playsound import playsound

REC_FILENAME = "recs.json"
PROMPT = ">>> "
TEMPI = ["fast", "mid", "slow"]

"""
    TODO:
1. make input nicer
2. catch exceptions
3. add search and view
4. when lsing print everything that is relevant(i.e. view)
"""


def get_tempo():
    return get_from_options("tempo", ["slow", "medium", "fast"])


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
    return get_from_options(filetype, files,accept_empty=True)


def get_chords():
    return get_until_empty("chords")


def get_feels():
    # TODO: change to get from options and add energy level
    return get_until_empty("feels")


def get_time_signature():
    return get_until_empty("time signature")

def add_new_composition(rec_file):
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
        if get_from_options("has line", ["yes", "no"], default='no') == "yes"
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

def get_recs_chords(recs):
    return [r["chords"] for r in recs]
    
def save_recs(recs):
    json.dump(recs, open(REC_FILENAME, "w"))
    

def main():
    rec_file = json.load(open(REC_FILENAME)) if os.path.isfile(REC_FILENAME) else []

    cmd = ''
    while cmd != "q":
        cmd = input(PROMPT).strip()
        match cmd:
            case "ls":
                for chords in get_recs_chords(rec_file):
                    print(chords)
            case "search":
                pass
            case "add":
                rec_file.append(add_new_composition(rec_file))
            case "rm":
                delete = get_from_options("recs", get_recs_chords(rec_file))
                rec_file = list(filter(lambda rec:rec["name"] != delete, rec_file))
            case "play":
                play = get_from_options("recs", get_recs_chords(rec_file))
                for rec in rec_file:
                    if rec["name"] == play:
                        playsound(rec["audio_file"])
            case "edit":
                pass
            case "save":
                save_recs(rec_file)
            case "help":
                print("""\tls - see all recordings\n\tsearch - query for recordings\n\tadd - add new recording\n\tsave - save to db\n\trm - delete recording(only from db)\n\tplay - play recording\n\tedit - edit recrding's metadata\n\tq - quit\n\thelp - this help""")
            case "q":
                save_recs(rec_file)


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


def get_from_options(category_name, options, add_new=False, accept_empty=False,default=''):
    if default not in options and default != '':
        raise 5
    if add_new:
        options.append("new")
    prompt_prefix = f">>> {category_name} - "
    optionlist = "\n".join([f"\t{n} - {'['if option == default else ''}{option}{']' if option == default else ''}" for n, option in enumerate(options)])
    prompt = f"{prompt_prefix}\n{optionlist}\n{PROMPT}"

    result = None
    while True:
        result = input(prompt)
        if (default != '' or accept_empty) and result == '':
                return default
        result = int(result)
        print(result)
        if result < len(options):
            if options[result] == "new":
                return input(f"enter new {category_name} - ")
            return options[int(result)]
        print("try again retard")


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
