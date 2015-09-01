# xpub

*A command-line client for the `uc-xromm` project.*

`xpub` is an alternative interface to the [`uc-xromm`](http://xromm.rcc.uchicago.edu/) data portal.  It's a CLI designed to let project members ...

* [create new studies](https://wiki.brown.edu/confluence/display/ctx/How+to+Create+a+New+Study)
* [create new trials](https://wiki.brown.edu/confluence/display/ctx/How+to+Create+Trials)
* initiate async file transfers to the Midway storage cluster
* collect metadata attributes of the files to be transferred


## Install

Since `xpub` is under active development we recommend cloning the source repo
and running the `setup.py` script in [development mode](https://pythonhosted.org/setuptools/setuptools.html#develop).

    > git clone https://github.com/rcc-uchicago/xpub.git
    > cd xpub
    > python setup.py develop

This should give you an `xpub` CLI:

    > which xpub
    /usr/local/bin/xpub

Having installed in developer mode, we only need to update the local repo (with
`git pull`) in order to update the `xpub` client.


## Rationale

Large file uploads via the `uc-xromm` web interface are time-consuming and
error prone due to timeouts and dropped connections.  Portal users are required to install a [java plugin](https://wiki.brown.edu/confluence/display/ctx/How+to+upload+files) and use a specific browser.  Further, the metadata attributes for uploaded files need to be manually entered at the time of upload.

In lieu of synchronous file-uploads via http and manual meta-data entry, the `xpub` client is designed for **asynchronous file transfers** (via a Globus executed transfer between pre-designated endpoints) and allows for semi-automated, **user-configurable metadata collection**.


## Metadata collection

The `uc-xromm` data portal let's users specify key attributes of each of the resources it manages: studies, trials, files.  For example, a **study** has the following attributes:

* a name
* a description
* a principal investigator
* a study leader
... etc.

This structured annotation (or "metadata") of its resources (or "data" items) makes it possible for users (and the portal itself) to search for resources with specific attributes.  E.g., show all studies run by this Principal Investigator.

The metadata attributes for a given resource are collected when the resource is created.  When creating a resource via the web portal this done through a web-based form.  When creating a resource via the `xpub` CLI, the user is led through a series of prompts for the relevant information.


## Config

The metadata collected about a resource can be specified in `xpub` config
files (`xpub/config/*.json`).  Instead of hard-coding a sequence of user prompts in the CLI itself, the various prompting sequences are specified in a config file for greater flexibility.  Users can thus specify additional attributes for resources as appropriate.  It's even possible for a user to define new "media types" (specific types of files) and their relevant attributes.  See `xpub/config/mediatypes` for examples.


#### How to add attributes to a config file

In order to add a new attribute to an existing configation file, open an existing config file in a text editor (e.g. vim) and add an object with the following key-value pairs to the prompts array:

    "key"     - key name used when sending the captured input value
    "text"    - text presented when prompting for input
    "info"    - additional information presented when called with `--verbose` switch
    "example" - example input (used in testing)
    "require" - True if input is required in XMA portal, False otherwise
    "type"    - indicates the type of prompt
    "store"   - array of backend persistence targets (use "xromm" to target the XMA portal)
    "regex"   - optional regular expression pattern to validate input

The value of `type` should be a string indicating the type of the input value expected.  The type options are ...

    TYPE     - EXPECTED INPUT VALUE
    'bool'   - boolean value (to prompt for `yes` or `no` input)
    'date'   - a date with the format `YYYY-MM-DD` (e.g. 2015-08-26)
    'text'   - open-ended string
    'list'   - a value from a fixed list of enumerated options or a user specified string
    'number' - a numeric value

If the `type` is a `list` then an additional key, `options`, should be included. `options` is an array of strings specifying the default options in the list. 


#### How to specify new mediatypes

Specifying a new mediatype is much like modifying an exisiting configuration file.  Begin by creating a new `.json` file in a text editor.  Create an object with the following key-value pairs:

    "description" - a string describing the mediatype
    "author"      - string specifying the creator of the mediatype config file
    "updated_at"  - string specifying when the file was last modified in form YYYY-MM-DD
    "prompts"     - array of config attribute objects 
    "version"     - string specifying the version of the configuration file
    "key"         - string specifying the key name used to identify this mediatype

#### Description of existing mediatypes
In addition to creating studies and trials, xpub can also record metadata about specified mediatypes.  Here, a mediatype is a specific type of file or set of filetypes associated with a particular type of data.  Presently, the following mediatypes have been defined: 

* vol (3D volume) 
* emg (electromyography recording)
* proc (processed file: 'UNDTFORM', 'MDLT', 'MayaCam')
* xray (xray video)
* grid (xray undistortion grid)
* calib (xray calibration object)
* video (standard video)
* NEV (event-based neural data)
* NSx (continuous neural data)
