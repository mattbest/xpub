#!/usr/bin/env python 
"""
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

def prompt_for(question, options=[], type='open', regex=None):
    if options:
        print question, "\n"
        for (i, opt) in enumerate(options):
            print("\t{} - {}".format(i, opt))
        print
        resp = int(raw_input('>>> '))
        if 0 <= resp < len(options):
            return options[resp]
        print("Please specify the number of one of the listed options!")
        return prompt_for(question, options, regex)

    if type == 'bool':
        regex = r'^[yn]$'
        question += " (`y` or `n`)"

    resp = raw_input(question + ' >>> ')
    if regex:
        rgx = re.compile(regex)
        if rgx.match(resp):
            return resp
        print("Invalid input")
        return prompt_for(question, regex=regex)
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
        key      = p['key']
        question = p['text']
        options  = p['enum']
        type     = p['type']
        regex    = re.compile(p['regex'])
        results['data'][key] = prompt_for(question, options, type, regex)

    print(json.dumps(results))
