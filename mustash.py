#!/usr/bin/python3
import json
import os
import pdb
from playsound import playsound
from audio_formats import AUDIO_FORMATS, SCORE_FORMATS
from emotions import EMOTIONS
from functools import partial
from itertools import chain

REC_FILENAME = "recs.json"
PROMPT = ">>> "
TEMPI = ["fast", "mid", "slow"]

"""
    TODO:
3. add search and view
5. split to files
4. when lsing print everything that is relevant(i.e. view)
"""


def try_until_good(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except ValueError:
            print("try again")


def get_tempo():
    return get_from_options("tempo",["slow","medium","fast"])


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
    return get_from_options(filetype, files, accept_empty=True)


def get_chords():
    return get_until_empty("chords")


def get_feels():
    keys_list = list(EMOTIONS.keys())
    final_choices = []
    while True:
        # pdb.set_trace()
        choices = get_from_options("feels", keys_list, accept_empty=True)
        if choices == [""]:
            break
        for choice in choices:
            for emotion in get_from_options(choice, EMOTIONS[choice], accept_empty=True):
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
        sigs: list[str] = get_until_empty("time signature")
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
    has_line = True if get_from_options("has line", ["no", "yes"], default="no") == ["yes"] else False
    
    feel = get_feels()
    composer = get_from_options(
        "composer", list(set(rec["composer"] for rec in rec_file)), add_new=True
    )
    used = get_from_options(
        "compsitions using this progression",
        list(chain(*map(lambda rec: rec["used"], rec_file))),
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
        """\tls - see all recordings\n\tsearch - query for recordings\n\tadd - add new recording\n\tsave - save to db\n\trm - delete recording(only from db)\n\tplay - play recording\n\tedit - edit recrding's metadata\n\tq - quit\n\thelp - this help"""
    )


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
                pass
            case "add":
                rec_file.append(add_new_composition(rec_file))
            case "rm":
                delete = get_from_options("recs", get_recs_chords(rec_file))
                rec_file = list(filter(lambda rec: rec["name"] != delete, rec_file))
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
                print_help()
            case "q":
                save_recs(rec_file)
            case _:
                print_help()


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


def get_from_options(
    category_name,
    options,
    add_new=False,
    accept_empty=False,
    default="",
):
    accept_empty = accept_empty or default != ""
    ALLOW_MULTIPLE_NOTIFY_MSG = "(enter space seperated list if multiple choices)"
    if default not in options and default != "":
        raise ValueError("default value has to be one of the options if it is given")
    elif default != "" and default in options:
        options[options.index(default)] = (
            "[" + options[options.index(default)].upper() + "]"
        )
    if add_new:
        options.append("new")
    prompt_prefix = f">>> {category_name} - {ALLOW_MULTIPLE_NOTIFY_MSG}"
    optionlist = "\n".join([f"\t{n} - {option}" for n, option in enumerate(options)])
    prompt = f"{prompt_prefix}\n{optionlist}\n{PROMPT}"

    result = None
    while True:
        result = input(prompt)
        if result == "" and not accept_empty:
            print("please try again retard")
            continue
        if not all(map(lambda x: x.isdigit(), result.split())):
            print("please try again retard")
            continue
        results = list(map(int, result.split()))
        if not all(map(lambda x: x < len(options), results)):
            print("please try again retard")
            continue

        if result == "" and accept_empty:
            return [default]

        text_results = []
        for entry in results:
            if options[entry] == "new":
                text_results.append(input(f"enter new {category_name} - "))
            else:
                text_results.append(options[entry])
        return text_results


def get_until_empty(category, options="", check=None):
    options_list = "\n".join(options)
    return list(
        filter(
            lambda x: x != "",
            dowhile(
                lambda: input(f"{PROMPT}{category} - \n\t{options_list}"),
                lambda things: things[-1] == "",
                True,
            ),
        )
    )


if __name__ == "__main__":
    main()
