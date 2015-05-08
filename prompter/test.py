import os
import json
from nose.tools import raises
from .main import Prompt, Prompter

# valid prompt dicts of various types for testing
valid_prompt_dicts = {

    # example of dict to prompt the user for text input
    'study': {  
        "key": "name",
        "text": "Name of study?",
        "info": "Your study name should only consist of alphanumeric characters and hyphens.",
        "type": "text",
        "options": [],
        "example": "pig-chewing-study",
        "require": True,
        "store": [
            "xromm"
        ],
        "regex": "\\w{3}"
    },

    # example of dict to prompt the user to choose from a list of options
    'leader': {
        "key": "leader",
        "text": "Name of study leader?",
        "info": "Specify the lab member most responsible for conducting this study.",
        "type": "list",
        "options": [            # list of options to be enumerated
            "Callum Ross",
            "Kazutaka Takashi"
        ],
        "example": "Kazutaka Takashi",
        "require": True,
        "store": [
            "xromm"
        ],
        "regex": "^\\d$"
    },

    # example of dict that prompts the user to choose yes or no
    'public': {
        "key": "meta_public",
        "text": "Metadata for this study is public?",
        "info": "Can the metadata for this study be made publicly available?",
        "type": "bool",
        "options": [],
        "example": True,        # json value should be `true` (lowercase)
        "require": True,
        "store": [
            "xromm"
        ],
        "regex": ""
    },

    # example of dict that prompts the user for numeric input
    'years': {
        "key": "years",
        "text": "Age in years?",
        "info": "",
        "type": "number",
        "example": 5,
        "require": True,
        "store": ["xromm"],
        "regex": ""
    }
}

def test_valid_prompts():
    '''Testing Prompt class'''
    prompt = Prompt(valid_prompt_dicts['study'])
    assert prompt.key is "name"
    assert prompt.type is "text"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == "pig-chewing-study", "should return example when testing"

    prompt = Prompt(valid_prompt_dicts['leader'])
    assert prompt.key is "leader"
    assert prompt.type is "list"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == "Kazutaka Takashi", "should return example when testing"

    prompt = Prompt(valid_prompt_dicts['public'])
    assert prompt.key is "meta_public"
    assert prompt.type is "bool"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == prompt.example, "should return example when testing"

    prompt = Prompt(valid_prompt_dicts['years'])
    assert prompt.key is "years"
    assert prompt.type is "number"
    assert prompt.require is True
    result = prompt(testing=True)
    assert result == prompt.example, "should return example when testing"

@raises(KeyError)
def test_missing_key():
    '''
    Testing prompt dict for required keys: KeyError expected.
    
    This prompt dict is missing an `example` key.

    '''
    d = {
        "key": "foo",
        "text": "Do you feel the foo?",
        "info": "",
        "type": "bool",
        "store": ["xromm"],
        "require": True
    }
    Prompt(d)                   # should raise KeyError
    
@raises(ValueError)
def test_invalid_type():
    '''Testing for invalid prompt type: ValueError expected'''
    d = {
        "key": "foo",
        "text": "What is the foo?",
        "info": "",
        "type": "foo",          # `foo` is not a valid prompt type
        "example": "bar",
        "require": True,
        "store": ["xromm"]
    }
    Prompt(d)                   # should raise ValueError
    
@raises(ValueError)
def test_invalid_store():
    '''Testing for invalid store value: ValueError expected'''
    d = {
        "key": "foo",
        "text": "Do you feel the foo?",
        "info": "",
        "type": "bool",         # `bool` is a valid prompt type
        "example": True,
        "require": True,
        "store": ["foo_db"]     # but `foo_db` is not a valid store value
    }
    Prompt(d)                   # should raise ValueError
    
def test_to_number():
    """Testing to_number() conversion"""
    d = {
        "key": "years",
        "text": "Age in years?",
        "info": "",
        "type": "number",
        "example": 5,
        "require": True,
        "store": ["xromm"]
    }
    prompt = Prompt(d)

    n = prompt.to_number('5')
    assert n is 5, "convert to integer"

    n = prompt.to_number('5.0')
    assert n == 5.0, "convert to float (if integer conversion fails)"

    n = prompt.to_number('+5.0')
    assert n == 5.0, "numeric sign is permitted"

    n = prompt.to_number('-5.0')
    assert n == -5.0, "numeric sign is permitted"

@raises(ValueError)
def test_to_number_err():
    """Testing to_number() conversion error"""
    d = {
        "key": "years",
        "text": "Age in years?",
        "info": "",
        "type": "number",
        "example": 5,
        "require": True,
        "store": ["xromm"]
    }
    prompt = Prompt(d)
    prompt.to_number('foo')


# load resource configuration file for the prompter
d = os.path.dirname(os.path.realpath(__file__))
local_config_path = os.path.join(d, '..', 'config')
CONFIG_DIR = os.environ.get('XROMM_CONFIG', local_config_path)
study_config = json.load(open(os.path.join(CONFIG_DIR, 'study.json')))

def test_prompter():
    '''
    Testing a Prompter instance.

    Note that when testing a prompter, the returned input values
    are just the example values given in the specified config file,
    For example, if prompting for a new study resource we'd use
    the `config/study.json` file to configure the prompter:

        {
            "key": "name",
            "text": "Name of study?",
            "example": "pig_chewing_study",     # input value to return
            ...                                 # when testing
        },
        {
            "key": "leader",
            "text": "Name of study leader?",
            "example": "Kazutaka Takashi",      # input value when testing
            ...
        },

    '''
    # this is the expected result based on the example inputs specified 
    # in our `study.json` config file
    expected = {
        "data": {
            "name": "pig-chewing-study", 
            "notes": "See `http://github.com/rcc-uchicago/xpub` for more info.", 
            "data_public": False, 
            "meta_public": True, 
            "pi": "Callum Ross", 
            "leader": "Kazutaka Takashi", 
            "desc": "A study that looks at how pigs chew stuff."
        }, 
        "version": "0.0.1", 
        "resource": "study"
    }

    prompt = Prompter(study_config, testing=True)
    prompt()
    assert prompt.results == expected

def test_prompter_required():
    '''
    Testing a Prompter instance for required prompts.

    Here we're initializing a Prompter the `required=True`, 
    which means we only want to be prompted for required prompts:

        Prompter(study_config, testing=True, required=True)

    Since the `notes` prompt in `$XROMM_CONFIG/study.json` is not
    required, the example value should not be included in the
    resulting `data` dict:

        {   
            "key": "notes",
            "text": "Additional notes or comments?",
            "require": false,
            ...
        }

    Compare `expected` below with that from the test above, which
    does in include an example value for `notes`.

    '''
    # this is the expected result based on the example inputs specified 
    # in our `study.json` config file
    expected = {
        "data": {
            "name": "pig-chewing-study", 
            "data_public": False, 
            "meta_public": True, 
            "pi": "Callum Ross", 
            "leader": "Kazutaka Takashi", 
            "desc": "A study that looks at how pigs chew stuff."
        }, 
        "version": "0.0.1", 
        "resource": "study"
    }

    prompt = Prompter(study_config, testing=True, required=True)
    prompt()
    print prompt.results
    assert prompt.results == expected
