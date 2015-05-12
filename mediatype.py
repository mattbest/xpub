from prompter import Prompt

# prompt user for a particular mediatype
def get_mediatype(testing=False):
    config = {  
        "key": "mediatype",
        "text": "What type of file is this?",
        "info": "Specify the mediatype of the file being transferred.",
        "type": "list",
        "options": [
            "emg (electromyography recording)",
            "cat (CAT scan)",
            "mov (standard video)",
            "xray (video, grid, or calibration object)",
            "other (none of the above)"
        ],
        "example": "mov (standard video)",
        "require": True,
        "store": [],
        "regex": ""
    }
    prompt = Prompt(config)                     # create prompt based on config
    input = prompt(fixed=True, testing=testing) # prompt for input
    choice = input.split(' ')[0]                # get mediatype from input
    return choice


if __name__ == '__main__':

    # prompt user to select appropriate mediatype
    choice = get_mediatype(testing=True)
    assert choice == 'mov'                      # given the example
