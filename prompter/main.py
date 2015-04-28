import re
import json


class Prompt:
    """
    Returns a Prompt object given a prompt dictionary.
    
    """
    def __init__(self, p): 

        for key in 'key text info example type store'.split(' '):
            if not (key in p):
                raise KeyError('prompt dict is missing `{}` key!'.format(key))

        store_options = ['xromm', 'ross_db']
        for s in p['store']:
            if not (s in store_options):
                msg = 'store={} | '.format(p['store'])
                msg += '`store` should only contain the following values: '
                msg += ', '.join(store_options)
                raise ValueError(msg)

        type_options = ['bool', 'open', 'enum', 'enum_open']
        type = p['type']
        if not (type in type_options):
            msg = 'type={} | '.format(type)
            msg += '`type` should be one of the following: '
            msg += ', '.join(type_options)
            raise ValueError(msg)

        self.__dict__.update(**p)

    def __call__(self, verbose=False, testing=False):
        """
        Run the prompt and return input response.

        """
        if testing:
            return self.example

        if verbose:
            print("\n{}".format(self.info))

        text = self.text    # text to prompt for input

        # if prompt type is boolean, prompt for `y` or `n` inputs
        if self.type == 'bool':
            text += " (`y` or `n`)"

        print("\n{}\n".format(text))

        # if prompt has enumerated options, enumerate them
        if self.enum:
            if self.type == 'enum_open':
                self.enum.append('Specify other')   # permit other input

            for (i, opt) in enumerate(self.enum):
                print("\t{} - {}".format(i, opt))
            print
            resp = self.get_input()

            try:
                choice = int(resp)
            except ValueError:
                if self.type == 'enum_open':
                    return resp     # assume they meant to input an alternative
                else:
                    choice = -1     # try again!

            if 0 <= choice < len(self.enum):
                result = self.enum[choice]
                if result == 'Specify other':
                    print("\n{}\n".format(text))
                    resp = self.get_input()
                return resp

            print("Please specify the number of one of the listed options!")
            return self.__call__(verbose, testing)

        # ... otherwise, for non-enumerated prompt types ...
        resp = self.get_input()

        # for booleans convert y/n responses to t/f
        if self.type == 'bool':
            if resp == 'y':
                return True
            elif resp == 'n':
                return False
            else:
                print("\nPlease specify `y` for yes or `n` for no!")
                return self.__call__(verbose, testing)

        # check response against supplied regex
        if self.regex:
            rgx = re.compile(self.regex)
            if rgx.match(resp):
                return resp
            print("Invalid input")
            return self.__call__(verbose, testing)

        return resp

    def get_input(self):
        """
        Prompt for raw input.

        """
        return raw_input('>>> ')
    


class Prompter:
    """
    Prompters are used to prompt for metadata given a resource
    config file.
    
    """
    def __init__(self, path, verbose=False, testing=False):
        """
        Initializes a Prompter given a path to a resource config file.

        """
        self.testing = testing              # true if testing
        self.verbose = verbose              # true for extra prompt info

        # load the JSON-formatted resource config file specified in path
        resource = json.load(open(path))

        # input will be collected for this resource under `data` key
        self.results = {
            'resource': resource['key'],    # name of resource
            'version':  resource['version'],
            'data': {}  # store k/v attributes for this resource here
        }

        # try initializing prompt dicts from loaded resource config file
        try:
            self.prompts = [Prompt(p) for p in resource['prompts']]
        except ValueError, KeyError:
            print "\nError initializing prompt dicts in {}!\n".format(path)
            raise

    def __call__(self):
        """
        Run each prompt and set value of each key to the collected input.
        
        """
        for prompt in self.prompts:
            result = prompt()
            self.set(prompt.key, result)

    def __str__(self):
        return json.dumps(self.results, indent=4)

    def set(self, key, result):
        "Set a key in collected data to result."
        self.results['data'][key] = result
