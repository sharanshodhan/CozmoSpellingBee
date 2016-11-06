import asyncio
import http.client
import cozmo
from cozmo.util import degrees

from tkinter import *
from tkinter import ttk

import ast
import json

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install Pillow` to install")


currentWord = '';
voice_pitch = 0.0
coz = None
conn = None;
server_ip = "localhost:5000"

userLetter = ''
userWord = ''

qtype = ''
sayword = ''

questime = '';

timer = None;

pollfortimer = False;

sayingword = False;
sayWords = [];

currentPlayerNumber = 0;
currentPlayerName = "";
lastPlayerNumber = 0;
_clock_font = None

gotWinner = False;

HappyTriggers = [cozmo.anim.Triggers.AcknowledgeFaceNamed]
SadTriggers = [cozmo.anim.Triggers.CubeMovedUpset]

try:
    _clock_font = ImageFont.truetype("arial.ttf", 24)
except IOError:
    try:
        _clock_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 24)
    except IOError:
        pass

async def start_world(coz, coz_conn):
    await say_word("Welcome to the first annual Cozmo Spelling Bee. My name is Roberto.");
    await say_word("I will be your judge for this competition. The rules are simple. Each of you will get a Cozmo partner. Your Cozmos will step up one at a time and get a word from me.");
    await say_word("You must spell the word correctly using the code in front of you. After every letter, wait for your Cozmo partner to say it before typing the next letter.");
    
async def say_word(word):
    global sayingword;
    global sayWords;
    if sayingword is False:
        sayingword = True;
        await coz.say_text(word, voice_pitch=voice_pitch, duration_scalar=1.5).wait_for_completed()
        while len(sayWords) != 0:
            await coz.say_text(sayWords[0], voice_pitch=voice_pitch, duration_scalar=1.5).wait_for_completed()
            sayWords.remove(sayWords[0]);
        sayingword = False;
    else:
        sayWords.append(word);

async def run(coz_conn):

    asyncio.set_event_loop(coz_conn._loop);
    global coz;
    global timer;

    coz = await coz_conn.wait_for_robot()

    await coz.set_head_angle(degrees(10.0), accel=50.0).wait_for_completed()

    await start_world(coz, coz_conn)

    await connect_to_server();

    asyncio.ensure_future(poll_active_player());
    asyncio.ensure_future(poll_winner());
    asyncio.ensure_future(poll_say_word());

    await asyncio.sleep(100000000);

async def connect_to_server():
    global conn;

    conn = http.client.HTTPConnection(server_ip);
    dict = {'judge': '1'}
    params = json.dumps(dict);
    headers = {"Content-type": "application/json"}
    conn.request("POST", "/startGame", params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close();

async def poll_active_player():
    global lastPlayerNumber
    global currentWord;
    global currentPlayerNumber;
    global sayword;
    global qtype;
    global questime;
    global currentPlayerName;

    while True:
        conn.request("GET", "/getCurrentPlayer")
        response = conn.getresponse()
        data = response.read()
        decodeddata = data.decode('UTF-8')
        datadict = ast.literal_eval(decodeddata);
        currentPlayerNumber = datadict['activePlayer'];
        currentPlayerName = '';
        if 'playerName' in datadict:
            currentPlayerName = datadict['playerName']
        if int(lastPlayerNumber) != int(currentPlayerNumber):
            currentWord = datadict['word'];
            qtype = datadict['type'];
            sayword = datadict['sayword'];
            lastPlayerNumber = currentPlayerNumber;
            questime = datadict['time'];
            if qtype == "Reverse":
                await say_word("Spell the word backwards")
            if qtype == "NoVowels":
                await say_word("Don't spell the vowels")
        await asyncio.sleep(1);
        conn.close();

async def poll_say_word():
    global questime;
    global pollfortimer;
    global currentPlayerName;

    while True:
        conn.request("GET", "/shouldSayWord")
        response = conn.getresponse()
        data = response.read()
        decodeddata = data.decode('UTF-8')
        datadict = ast.literal_eval(decodeddata);
        if datadict['word'] != '':
            if datadict['newWord'] == 'true':
                await say_word(currentPlayerName + ". Your word is. " + datadict['word'])
            else:
                await say_word(datadict['word'])

        await asyncio.sleep(0.5);
        conn.close()

async def poll_winner():

    global currentPlayerNumber;
    global gotWinner;

    while gotWinner is False:
        conn.request("GET", "/getWinner")
        response = conn.getresponse()
        data = response.read()
        decodeddata = data.decode('UTF-8')
        datadict = ast.literal_eval(decodeddata);
        swinner = int(datadict['winner']);
        if swinner != 0:
            gotWinner = True;
            await say_word("Player " + str(swinner) + " Won");
        await asyncio.sleep(1);
        conn.close();

async def pollTimeUp():
    global pollfortimer;

    while pollfortimer:
        conn.request("GET", "/isTimeUpJudge")
        response = conn.getresponse()
        data = response.read()
        decodedData = data.decode('UTF-8')
        datadict = ast.literal_eval(decodedData);
        istimeup = datadict['timeUp'];
        if istimeup == 'true':
            pollfortimer = False;
            await coz.say_text("Time Up", voice_pitch=voice_pitch, duration_scalar=2).wait_for_completed()
        await asyncio.sleep(0.2);
        conn.close();

class test():
    def __init__(self, master=None):
        self.entry = None;
        self.render();

    def render(self):
        self.root = Tk()

        label = ttk.Label(self.root,
                          text='Annual Cozmo Spelling Bee')  # creates label object but not displayed yet
        label.pack()  # Displays text

        label = ttk.Label(self.root, text='Enter IP')  # creates label object but not displayed yet
        label.pack()  # Displays text

        self.serverentry = ttk.Entry(self.root, width=30)
        self.serverentry.insert(0, server_ip);
        self.serverentry.pack()

        button = ttk.Button(self.root, text='Enter', command=self.ButtonPressed)
        button.pack()
        button['text']
        'Enter'

        self.root.mainloop();

    def ButtonPressed(self):
        global server_ip;

        server_ip = self.serverentry.get();

        self.root.destroy();
        cozmo.setup_basic_logging()
        cozmo.connect(run)

app = test();

# if __name__ == '__main__':
#     cozmo.setup_basic_logging()
#     cozmo.connect(run)
