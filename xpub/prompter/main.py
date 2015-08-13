import re
import datetime 


class Prompt:
    """
    Returns a Prompt object given a prompt dictionary.
    
    """
    def __init__(self, p): 
        """
        Initialize a Prompt object.

        `p` should be dict with the relevant keys needed for prompting:
        
          `key`     - key name used when sending the captured input value
          `text`    - text presented when prompting for input
          `info`    - additional info presented with `--verbose` switch
          `example` - example input (used when testing)
          `require` - True if input is required, False otherwise
          `type`    - indicating type of prompt
          `store`   - array of backend persistence targets
          `regex`   - optional regex pattern to validate input

        The value of `p['type']` should be a string indicating the 
        type of the input value expected. The type options are ...
            
             TYPE  - EXPECTED INPUT VALUE
            `bool` - boolean value (to prompt for `yes` or `no` input)
            `date` - a date value with format `YYYY-MM-DD` (2014-04-28)
            `text` - open-ended string
            `list` - a value from a fixed list of enumerated options
                     or a user specified value
            `number` - a numeric value

        The value of `p['store']` should be an array of string values,
        where the string values indicate the backend datastores to 
        which a given key/value pair should be persisted (`xromm` and/or
        `ross_db`).  For example, if you're prompting for something 
        exclusively for the xromm portal's database, you'd set
        `p['store'] = ['xromm']`.  If you're prompting for something
        recognized by both the xromm db and the internal database
        used by the Ross Lab, you'd set `p['store'] = ['xromm', 'ross_db']`.

        """
        # ensure prompt dict has all the necessary keys
        for key in 'key text info example require type store'.split(' '):
            if not (key in p):
                msg = 'prompt dict is missing `{}` key!'.format(key)
                print p
                raise KeyError(msg)

        # check that values in `store` array are valid
        store_options = ['xromm', 'ross_db', 'hatabase']    
        for s in p['store']:
            if not (s in store_options):
                msg = 'store={} | '.format(p['store'])
                msg += '`store` should only contain the following values: '
                msg += ', '.join(store_options)
                raise ValueError(msg)

        # check that `type` value is valid
        type_options = ['bool', 'date', 'text', 'list', 'number']
        type = p['type']
        if not (type in type_options):
            msg = 'type={} | '.format(type)
            msg += '`type` should be one of the following: '
            msg += ', '.join(type_options)
            raise ValueError(msg)

        # regex for checking date format
        self.yyyy_mm_dd = re.compile(r'^20\d\d-[0-2]\d-[0-3]\d$')

        # make the dict keys of `p` accessible as properties: `self.name`
        self.__dict__.update(**p)


    def __call__(self, verbose=False, testing=False, fixed=False):
        """
        Run the prompt and return input response (or the supplied
        prompt example if testing).

        If `verbose` is true, additional usage/info is presented 
        when prompting.

        If `testing` is true, example input is returned.

        If `fixed` is true, users can only specify one of the
        enumerated options for prompts of type `list`.

        """
        if testing:
            return self.example

        if verbose:
            print("\n{}".format(self.info))

        text = self.text    # text to prompt for input

        # if prompt type is boolean, prompt for `y` or `n` inputs
        if self.type == 'bool':
            text += " (`y` or `n`)"

        # for date inputs, provide today's date as default option
        if self.type == 'date':
            text += " (hit return for `{}`)".format(self.today())

        print("\n{}\n".format(text))

        # if prompt has options, enumerate them
        if self.options:
            return self.enumerate_options(fixed)

        # ... otherwise, for other prompt types ...
        resp = self.get_input()

        # return null response if no input given and not required
        if not(self.require) and not(resp):
            return None

        # for booleans, convert y/n response to t/f
        if self.type == 'bool':
            if resp == 'y':
                return True
            elif resp == 'n':
                return False
            else:
                print("\nPlease specify `y` for yes or `n` for no!")
                return self.__call__(verbose, testing)

        # for numbers, convert response to a number (int or float)
        if self.type == 'number':
            try:
                return self.to_number(resp)
            except ValueError:
                print("\nInvalid numeric input. Please re-enter value")
                return self.__call__(verbose, testing)

        if self.type == 'date':
            if resp and not self.valid_date(resp):
                print("\nInvalid date input. Please use `YYYY-MM-DD` format.")
                return self.__call__(verbose, testing)
            else:
                return self.today()

        # finally, check response against any supplied regex pattern
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
    

    def to_number(self, input):
        """
        Convert input to number.

        """
        try:
            n = int(input)
            return n
        except ValueError:
            n = float(input)
            return n


    def today(self):
        """
        Return today's date as an ISO-formatted string: YYYY-MM-DD.

        """
        return datetime.date.today().isoformat()


    def valid_date(self, input):
        """
        Check that input is in valid date format (YYYY-MM-DD).

        """
        return self.yyyy_mm_dd.match(input)


    def enumerate_options(self, fixed=False):
        """
        Enumerate provided options for user to select.
        
        If `fixed` is True, do not include option to specify
        alternative input.

        """
        options = self.options[:]           # create a copy of options
        if not fixed:
            options.append('Specify other') # permit other input

        for (i, opt) in enumerate(options):
            print("\t{} - {}".format(i, opt))
        print
        resp = self.get_input()

        try:
            choice = int(resp)
        except ValueError:
            return resp     # assume they meant to input an alternative

        if 0 <= choice < len(options):
            result = options[choice]
            if result == 'Specify other':
                print("\n{}\n".format(self.text))
                result = self.get_input()
                if not result:              # no response given
                    if self.require:
                        print("\nResponse required!")
                        return self.__call__()
                    else:
                        return None     # not required

            return result

        print("Please specify the number of one of the listed options!")
        return self.__call__()


class Prompter:
    """
    Prompters are used to prompt for metadata given a resource
    config file.
    
    """
    def __init__(self, config, verbose=False, testing=False, required=False):
        """
        Initializes a Prompter given a path to a resource config file.

        """
        self.testing = testing              # true if testing
        self.verbose = verbose              # true for extra prompt info
        self.config_revisions = False       # true with new input options
        self.config = config

        # input will be collected for this resource under `data` key
        self.results = {
            'resource': config['key'],    # name of resource
            'version':  config['version'],
            'data': {}  # store k/v attributes for this resource here
        }

        # try initializing prompt dicts from loaded resource config file
        try:
            if required:                    # only include required prompts
                self.prompts = [Prompt(p) for p in config['prompts'] 
                                                    if p['require']]

            else:                           # include all prompts
                self.prompts = [Prompt(p) for p in config['prompts']]

        except ValueError, KeyError:
            err = "\nError initializing prompt dicts in {} config!\n"
            print err.format(config['key'])
            raise

    def __call__(self):
        """
        Run each prompt and set value of each key to the collected input.
        
        """
        for i, prompt in enumerate(self.prompts):
            result = prompt(testing=self.testing)

            # check for new input options to cache
            if result and prompt.type == 'list' \
                      and result not in prompt.options:
                self.config['prompts'][i]['options'].append(result)
                self.config_revisions = True
                
            self.set(prompt.key, result)

    def set(self, key, result):
        "Set a key in collected data to result."
        self.results['data'][key] = result
