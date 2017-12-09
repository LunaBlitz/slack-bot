import os
import time
from slackclient import SlackClient
from collections import defaultdict
import pdb
import logging
import random

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN_ZORA")
AT_BOT = "<@" + BOT_ID + ">"
logger = logging.getLogger(__name__)
# instantiate Slack
slack_client = SlackClient(SLACK_TOKEN)


def ditto_cmd(cmd):
    """
    returns the same message as the user sent, just without the first word (command name)
    :param cmd: str, message to be repeated
    :return: str, message to be printed back (same as original)
    """
    return " ".join(cmd.split()[1:])

def joke_cmd(cmd):
    """
    CURRENT:
    pulls random chuck norris jokes for zora to tell users when they use the command joke. 
    the purpose of this is to make people laugh and get more confomtable using 
    zora and having fun with her.
    
    PLANS TO EXTEND:
    add different kinds of joke api's to randomly pick from to get a different joke each time 

    #ToDo
    Add more API endpoints for jokes 
    -IT joke API (url)
    -DOG joke API (url)


    AUTHOR:@Luna
    """
     response = requests.get("https://api.chucknorris.io/jokes/random") # pulls api for random chuch norris jokes 
     response.raise_for_status() # to raise an exception for error codes

     json_data = response.json() #pulls json data from the site 

     joke = json_data.get("value") #pulls json value which is the actual joke 

     return joke


def cats_cmd(cmd):
    eats = random.randint(1,5)

    if eats == 1:
        return "Cats are Yummy! No kittys here."
    else:
        # send cat picture
        return "<Cat Picture>"

def greet_cmd(cmd):
    greetings = ['hi', "hello", "hola", "konichiwa"]
    return greetings.random.choice()


def startproject_cmd(cmd):
    """
    Shows procedure used to start a new project on a certain platform
    :param cmd: str, name of OS
    :return: str, list of commands
    """
    if len(cmd.split) > 1:
        project_os = cmd.split()[1].lower()
    else:
        return "Please enter an OS!"
    if project_os == "windows":
        response = "These are the commands to start a new Windows Project"
    elif project_os == "mac":
        response = "Different start project commands for mac"
    elif project_os == "linux":
        response = "Linux commands for new project"
    else:
        response = "Sorry, I only know Mac, Linux and Windows I don't know what {} is".format(project_os)
    return response


def help_cmd(cmd):
    """
    Shows help for certain command, if none given shows help for every command
    :param cmd: str, name of command (optional)
    :return: str, help list
    """
    split = cmd.split()
    if len(split) == 1:
        lines = ["{}: {}".format(cmd.name, cmd.help_text) for cmd in Command.get.values()]
    elif split[1] in Command.get:
        cmd = Command.get[split[1].lower()]
        lines = ["{}: {}".format(cmd.name, cmd.help_text)]
    else:
        lines = ["Sorry, this command is not found."]
    return "\n".join(lines)


class Command:
    """
    Class for commands, used for easier access
    """
    get = defaultdict(lambda: None)  # this is the list of all commands. If command is searched but not in the dict,
    # None is returned

    def __init__(self, func, name, help_text):
        """
        Sets all the parameters & adds the command to list of all
        :param func: pointer to the function
        :param name: str, name of the function
        :param help_text: str, help text to be displayed when help command is called
        """
        self.func = func
        self.name = name
        self.help_text = help_text
        Command.get[name] = self

    def execute(self, message):
        """
        Executes the function it is pointing to.
        :param message: str, user's message, is passed to the function
        :return: str, returns whatever the function returns
        """
        return self.func(message)


def handle_command(text, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    cmd_name = text.split()[0].lower()
    cmd = Command.get[cmd_name]  # Get the command's name and the appropriate instance of Command class. None if
    # there is no instance with such name

    if cmd:
        response = cmd.execute(text)
    else:
        response = "Sorry, I have not been trained to do that yet."

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                logger.info("Zora command called: " + output.get("text"))
                command = output['text'].split(AT_BOT)[1].strip()
                channel = output['channel']
                return command, channel
    return None, None


def define_commands():
    """
    Defines all commands. Shall only be executed once, when the code starts.
    :return: None
    """
    Command(ditto_cmd,
            "ditto",
            "Repeats said text")
    Command(startproject_cmd,
            "startproject",
            "How to start a project on different OS's")
    Command(help_cmd,
            "help",
            "Displays help for given command or all if none given.")
    Command(cats_cmd, 
            "yummy",
            "Returns a picture of a cat")
    Command(greet_cmd, 
            "hi",
            "Says hi in a random in a random language")  
     Command(joke_cmd, 
            "joke", 
            "tells zora to tell people a random joke")



def main():
    define_commands()

    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        logger.info("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        logger.error("Connection failed. Invalid Slack token or bot ID?")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

# ----vv---- used for local testing

# if __name__ == "__main__":
#     define_commands()
#
#     def a(x, **kwargs):
#         print(kwargs["text"])
#
#     slack_client.api_call = a
#
#     while True:
#         handle_command(input("Enter the command:  "), "a")
