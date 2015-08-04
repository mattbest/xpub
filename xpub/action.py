import os
import json
import requests
from datetime import datetime
from prompter import Prompt


# save/update a json config file (at `path`) with config `data`
def save_json(data, path):
    data['updated_at'] = datetime.now().isoformat() + 'Z'
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


# possible actions to take with collected input  . . .

def view(results): 
    print json.dumps(results, indent=4)
    print '<<< COLLECTED METADATA'

def save(results):                              
    path = os.path.join(os.getcwd(), 'input.json')
    save_json(results, path)
    print "input saved to", path

def send(results): 
    resource = results['resource']
    version = results['version']
    path = 'studies/'

    if resource.startswith('file'):
        study_trial  = results['data']['study_trial']
        if '/' in study_trial:                      # study/trial
            study, trial = study_trial.split('/')
            path += '{}/trials/{}/'.format(study, trial)
        else:
            study, trial = study_trial, ''          # no trial name
            path += '{}/'.format(study)

    elif resource is 'trial':
        path += results['data']['study'] + '/trials/'

    url = 'http://xromm.rcc.uchicago/api/v{}/{}'.format(version, path)
    print "sending to", url

    # comment out next two lines when backend service in place!
    url = "http://httpbin.org/post"     
    print "\n... actually, we're sending to", url, "for testing purposes!"
    resp = requests.post(url, data=json.dumps(results))
    print(resp.text)

def quit(results): 
    raise SystemExit


# dict of possible action choices (keys) and action functions (values)
actions = {
    "view": view,
    "save": save,
    "send": send,
    "quit": quit
}

# prompt configuration, to prompt for an action
config = {  
    "key": "action",
    "text": "What to do with the collected metadata?",
    "info": "What do you want to do with these inputs?",
    "type": "list",
    "options": [
        "view (look it over before doing anything else)",
        "save (save it to a file)",
        "send (send it off to the `xromm` server)",
        "quit (just discard it)"
    ],
    "example": "quit (just discard it)",
    "require": True,
    "store": [],
    "regex": ""
}

# prompt the user for the action to take on the `results` dict
def prompt_for_action(results, path=None):
    if path:
        results['file_name'] = os.path.basename(path)
    prompt = Prompt(config)                 # create prompt based on config
    input = prompt(fixed=True)              # prompt for input
    choice = input.split(' ')[0]            # get action from input
    actions[choice](results)                # do the chosen action
    if choice == 'view':
        prompt_for_action(results)          # prompt again


if __name__ == '__main__':

    # example results
    results = dict(resource="trial", study="pig-chewing-study")

    # prompt user to select action to take on results and then do it
    prompt_for_action(results)
