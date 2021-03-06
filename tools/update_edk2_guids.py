# SPDX-License-Identifier: MIT

import argparse
import glob
import os
import re
import shutil

DATA_PATH = os.path.join("..", "conf")
IDA_GUIDS = os.path.join("..", "ida_plugin", "uefi_analyser", "guids")


def get_py(string):
    new_string = "edk2_guids = {\n"

    replace_table = {
        "{": "[",
        "}": "]",
        "#": "\t#",
        "=": ":",
        "]\n": "],\n",
    }

    re_table = {
        r"\ng": "\n\t'g",
        r" +:": ":",
        r":": "' :",
        r"\]\]": "]",
        r"\] +\]": "]",
        r", +\[": ",",
        r",\[": ",",
    }

    for key in replace_table:
        string = string.replace(key, replace_table[key])
    new_string += string + "}"
    for regexp in re_table:
        new_string = re.sub(regexp, re_table[regexp], new_string)
    return new_string


def get_guids_list(edk2_path, data_path):
    if not os.path.isdir(edk2_path):
        print("[-] Error, check edk2 path")
        return False
    tmpl = os.path.join(edk2_path, "*", "*.dec")
    dec_files = glob.glob(tmpl)
    if not len(dec_files):
        print("[-] Error, *.dec files list is empty")
        return False
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)
    regexp = re.compile(r"g.+=.+{.+}")
    conf_content = ""
    for dec_file in dec_files:
        with open(dec_file, "r") as dec:
            guids_list = re.findall(regexp, dec.read())
            conf_content += f"# Guids from {dec_file} file\n"
            for guid in guids_list:
                conf_content += f"{guid}\n"
    with open(os.path.join(DATA_PATH, "edk2_guids.conf"), "w") as conf:
        conf.write(
            "# This file was automatically generated with update_edk2_guids.py script\n"
        )
        conf.write(conf_content)
    py_content = get_py(conf_content)
    with open(os.path.join(DATA_PATH, "edk2_guids.py"), "w") as conf:
        conf.write(
            "# This file was automatically generated with update_edk2_guids.py script\n"
        )
        conf.write(py_content)
    return True


def update(edk2_path, data_path, guids_path):
    if get_guids_list(edk2_path, data_path):
        shutil.copy(
            os.path.join(data_path, "edk2_guids.py"),
            os.path.join(guids_path, "edk2_guids.py"),
        )
        conf_path = os.path.join(data_path, "edk2_guids.conf")
        py_path = os.path.join(data_path, "edk2_guids.py")
        print(f"[*] Files {conf_path}, {py_path} was successfully updated")
        return True
    return False


def main():
    program = f"python {os.path.basename(__file__)}"
    parser = argparse.ArgumentParser(
        description="Script to update the edk2_guids.py file", prog=program
    )
    parser.add_argument("edk2_path", type=str, help="the path to EDK2 directory")

    args = parser.parse_args()

    if get_guids_list(args.edk2_path, DATA_PATH):
        shutil.copyfile(
            os.path.join(DATA_PATH, "edk2_guids.py"),
            os.path.join(IDA_GUIDS, "edk2_guids.py"),
        )
        conf_path = os.path.join(DATA_PATH, "edk2_guids.conf")
        py_path = os.path.join(DATA_PATH, "edk2_guids.py")
        print(f"[*] Files {conf_path}, {py_path} was successfully updated")


if __name__ == "__main__":
    main()
