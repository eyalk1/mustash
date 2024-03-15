#!/usr/bin/python3
import itertools
import json
import os
import pdb
from playsound import playsound
from audio_formats import AUDIO_FORMATS, SCORE_FORMATS
from emotions import EMOTIONS
from functools import partial
from itertools import chain
from utils import (
    get_from_options,
    get_until_empty,
    not_empty,
    try_until_good,
    get_files_from_curdir,
    get_attr,
)
from common import PROMPT, REC_FILENAME

TEMPI = ["fast", "mid", "slow"]

"""
    TODO:
1. make audio playing seekable
2. 
"""


def get_tempo():
    return get_from_options("tempo", ["slow", "medium", "fast"])


def get_chords():
    return [s.split() for s in get_until_empty("chords")]


def get_feels():
    keys_list = list(EMOTIONS.keys())
    final_choices = []
    while True:
        choices = get_from_options("feels", keys_list, accept_empty=True)
        if choices == [""]:
            break
        for choice in choices:
            for emotion in get_from_options(
                choice, EMOTIONS[choice], accept_empty=True
            ):
                final_choices.append(emotion)
        if len(final_choices) > 0 and final_choices[-1] == [""]:
            final_choices = final_choices[:-1]
            break
    return final_choices


def get_time_signature():
    def check_signature(sig):
        if sig.count("/") != 1:
            print(f"sig - {sig} is badly formed - use a single /")
            return False
        up, down = sig.split("/")
        possible_denominators = ["2", "4", "8", "16", "32"]
        if down not in possible_denominators:
            print(
                f"sig - {sig} is badly formed - the denominator should be one of {possible_denominators}"
            )
            return False
        return True

    while True:
        sigs = input(
            f"{PROMPT}enter space separated list of time signature - \n\t"
        ).split()
        if all(map(check_signature, sigs)):
            break

    return sigs


def get_length():
    return float(input(f"{PROMPT}length - "))


def check_audio_file(rec_file, extension_list, filename):
    return (
        filename not in [s["audio_file"] for s in rec_file]
        and os.path.splitext(filename)[1] in extension_list
    )


def add_new_composition(rec_file):
    tempo = get_tempo()
    audio_file = get_files_from_curdir(
        "audio_file", partial(check_audio_file, rec_file, AUDIO_FORMATS)
    )
    score_file = get_files_from_curdir(
        "score_file", partial(check_audio_file, rec_file, SCORE_FORMATS)
    )
    chords = get_chords()
    has_line = (
        True
        if get_from_options("has line", ["no", "yes"], default="no") == ["yes"]
        else False
    )

    feel = get_feels()
    composer = get_from_options(
        "composer",
        list(set(e for rec in rec_file for e in rec["composer"])),
        add_new=True,
    )
    used = get_from_options(
        "compsitions using this progression",
        list(set(e for rec in rec_file for e in rec["used"])),
        add_new=True,
        accept_empty=True,
    )
    length = try_until_good(get_length)
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


def print_help():
    print(
        """\tls - see all recordings\n\tsearch - query for recordings\n\tadd - add new recording\n\tsave - save to db\n\trm - delete recording(only from db)\n\tq - quit\n\thelp - this help"""
    )


def search(rec_file):
    if len(rec_file) == 0:
        print(f"{PROMPT}no recordings in db")
        return []

    search_rec = {}
    chosen_attributes = get_from_options("attributes", list(rec_file[0].keys()))
    for attribute in chosen_attributes:
        possible_values = sorted(filter(not_empty, map(get_attr(attribute), rec_file)))
        possible_values = list(k for k, _ in itertools.groupby(possible_values))
        print(possible_values)
        if possible_values == []:
            print(f"no options for {attribute}")
            continue
        values = get_from_options(attribute, possible_values)
        if values == [""]:
            print(f"no options for {attribute}")
            continue
        search_rec[attribute] = values

    possible_searchs = []
    for rec in rec_file:
        is_pass = True
        for key, val in search_rec.items():
            if rec[key] not in val:
                is_pass = False
                break
        if is_pass:
            possible_searchs.append(rec)

    return get_from_options("search results", possible_searchs, accept_empty=True)


def view(rec, rec_file):
    print(rec)
    while True:
        action = get_from_options(
            "what do?", ["play", "edit", "return"], accept_empty=True
        )
        if action == []:
            continue
        action = action[0]
        match action:
            case "play":
                if not_empty(rec["audio_file"]):
                    playsound(rec["audio_file"][0])
                else:
                    print("no audio!")
            case "edit":
                chosen_attributes = get_from_options("attributes", list(rec.keys()))
                for attribute in chosen_attributes:
                    match attribute:
                        case "tempo":
                            rec["tempo"] = get_tempo()
                        case "audio_file":
                            rec["audio_file"] = get_files_from_curdir(
                                "audio_file",
                                partial(check_audio_file, rec_file, AUDIO_FORMATS),
                            )
                        case "score_file":
                            rec["score_file"] = get_files_from_curdir(
                                "score_file",
                                partial(check_audio_file, rec_file, SCORE_FORMATS),
                            )
                        case "chords":
                            rec["chords"] = get_chords()
                        case "has_line":
                            rec["has_line"] = (
                                True
                                if get_from_options(
                                    "has line", ["no", "yes"], default="no"
                                )
                                == ["yes"]
                                else False
                            )
                        case "feel":
                            rec["feel"] = get_feels()
                        case "composer":
                            rec["composer"] = get_from_options(
                                "composer",
                                list(
                                    set(e for rec in rec_file for e in rec["composer"])
                                ),
                                add_new=True,
                            )
                        case "used":
                            rec["used"] = get_from_options(
                                "compsitions using this progression",
                                list(set(e for rec in rec_file for e in rec["used"])),
                                add_new=True,
                                accept_empty=True,
                            )
                        case "length":
                            rec["length"] = try_until_good(get_length)
                        case "time_signature":
                            rec["time_signature"] = get_time_signature()
            case "return":
                return


def main():
    rec_file = json.load(open(REC_FILENAME)) if os.path.isfile(REC_FILENAME) else []

    cmd = ""
    while cmd != "q":
        cmd = input(PROMPT).strip()
        match cmd:
            case "ls":
                for chords in get_recs_chords(rec_file):
                    print(chords)
            case "search":
                result = search(rec_file)
                if result != []:
                    view(result[0], rec_file)
                else:
                    print(f"{PROMPT}no recording suits your search")
            case "add":
                rec_file.append(add_new_composition(rec_file))
                save_recs(rec_file)
            case "rm":
                delete = get_from_options("recs", get_recs_chords(rec_file))
                rec_file = list(filter(lambda rec: rec["name"] != delete, rec_file))
            case "save":
                save_recs(rec_file)
            case "help":
                print_help()
            case "q":
                save_recs(rec_file)
            case _:
                print_help()


if __name__ == "__main__":
    main()
