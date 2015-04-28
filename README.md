# xpub

*A command-line client for the `uc-xromm` project.*

`xpub` is an alternative interface to the [`uc-xromm`](http://xromm.rcc.uchicago.edu/) data portal.  It's a CLI designed to let project members ...

* [create new studies](https://wiki.brown.edu/confluence/display/ctx/How+to+Create+a+New+Study)
* [create new trials](https://wiki.brown.edu/confluence/display/ctx/How+to+Create+Trials)
* initiate async file transfers to the Midway storage cluster
* collect metadata attributes of the files to be transferred


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
files (`config/*.json`).  Instead of hard-coding a sequence of user prompts in the CLI itself, the various prompting sequences are specified in a config file for greater flexibility.  Users can thus specify additional attributes for resources as appropriate.  It's even possible for a user to define new "media types" (specific types of files) and their relevant attributes.

> TODO: give an overview of how to add attributes and new media types to the
> config file.
