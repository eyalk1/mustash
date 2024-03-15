from common import PROMPT, REC_FILENAME
import os


def not_empty(thing):
    return thing != [] and thing != "" and thing != [""]


def get_attr(attr):
    def get_attr_imp(dic):
        return dic[attr]

    return get_attr_imp


def try_until_good(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except ValueError:
            print("try again")


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


def get_from_options(
    category_name,
    options,
    add_new=False,
    accept_empty=False,
    default="",
):
    if options == []:
        return []
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
