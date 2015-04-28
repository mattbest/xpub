#!/usr/bin/env python 
"""
            / 
  )( /) (/ () 
    /       

A CLI for `xromm.uchicago.edu`.

Prompts the user for metadata when creating a study or trial or 
transferring a file.

"""
import re
import json
import argparse

parser = argparse.ArgumentParser(version="0.1", description=__doc__)
parser.add_argument('--study', 
                    action="store_true", 
                    help="Create a new study")
parser.add_argument('--trial', 
                    action="store_true",
                    help="Create a new trial")
parser.add_argument('--file', 
                    action="store",
                    help="Transfer a file")

args = parser.parse_args()


class Prompt:
    "Returns a Prompt object given a prompt dictionary."
    def __init__(self, p): self.__dict__.update(**p)


# Prompt for the supplied prompt, which should be a Prompt instance.
def prompt_for(prompt):

    # if prompt has enumerated options, enumerate them
    if prompt.enum:
        print prompt.text, "\n"
        for (i, opt) in enumerate(prompt.enum):
            print("\t{} - {}".format(i, opt))
        print
        resp = int(raw_input('>>> '))
        if 0 <= resp < len(prompt.enum):
            return prompt.enum[resp]
        print("Please specify the number of one of the listed options!")
        return prompt_for(prompt)

    # if prompt type is boolean, prompt for `y` or `n` inputs
    if prompt.type == 'bool':
        prompt.text += " (`y` or `n`)"

    resp = raw_input(prompt.text + ' >>> ')

    if prompt.type == 'bool':
        if resp == 'y':
            return True
        if resp == 'n':
            return False

    # check response against supplied regex
    if prompt.regex:
        rgx = re.compile(prompt.regex)
        if rgx.match(resp):
            return resp
        print("Invalid input")
        return prompt_for(prompt)

    return resp


if __name__ == '__main__':

    if args.study:
        resource = json.load(open('config/study.json'))
    elif args.trial:
        resource = json.load(open('config/trial.json'))
    elif args.file:
        resource = json.load(open('config/file.json'))
    else:
        parser.print_help()
        raise SystemExit
        

    results = {
        'resource': resource['key'],
        'version':  resource['version'],
        'data': {}
    }

    for p in resource['prompts']:
        prompt = Prompt(p)
        results['data'][prompt.key] = prompt_for(prompt)

    print(json.dumps(results))
