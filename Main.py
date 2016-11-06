import asyncio
import http.client
import cozmo
from cozmo.util import degrees
from tkinter import *
from tkinter import ttk
import ast
import json
import random

currentWord = '';
speakWord = '';
type = '';

voice_pitch = 0.0
coz = None
waitingBool = False
conn = None;
server_ip = "128.237.194.4:5000"

morseCodes = ['.-','-...','-.-.','-..','.','..-.','--.','....','..','.---','-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-','..-','...-','.--','-..-','-.--','--..']
cubes = []
cubeObjectIds = []

userLetter = ''
userWord = ''
colors = [0xff000000,0x00ff0000,0x0000ff00]
currentLetterLength = 0

currentPlayerNumber = -1;
currentPlayerName = "John";
ismyturnactive = False;
takeInput = False;

pollfortimer = False;

foundWinner = False;

sentResponseToServer = False;

HappyTriggers = [
    cozmo.anim.Triggers.AcknowledgeFaceNamed,
    cozmo.anim.Triggers.CubePounceWinHand,
    cozmo.anim.Triggers.ReactToBlockPickupSuccess,
    cozmo.anim.Triggers.RollBlockSuccess,
    cozmo.anim.Triggers.SparkSuccess,
    cozmo.anim.Triggers.StackBlocksSuccess
]
SadTriggers = [
    cozmo.anim.Triggers.CubeMovedUpset,
    cozmo.anim.Triggers.CubePounceLoseSession,
    cozmo.anim.Triggers.CubePounceLoseHand,
    cozmo.anim.Triggers.DriveStartAngry,
    cozmo.anim.Triggers.FrustratedByFailure,
    cozmo.anim.Triggers.OnSimonPlayerWin
]

WinAnimationTrigger = cozmo.anim.Triggers.KnockOverSuccess
LoseAnimationTrigger = cozmo.anim.Triggers.OnSpeedtapGamePlayerWinHighIntensity

async def blinkCubes(coz_conn, cubes):

    for i in range(0,20):
        for cube in cubes:
            cube.set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[i%3])))
        await asyncio.sleep(0.1)

    cubes[0].set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[0])))
    cubes[1].set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[1])))
    cubes[2].set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[2])))


async def startWorld(coz, coz_conn):
    await coz.say_text("Hello, " + currentPlayerName, voice_pitch=voice_pitch, duration_scalar=1.2).wait_for_completed()
    find_cubes = 3;

    global cubes;
    try:
        cubes = await coz.world.wait_until_observe_num_objects(num=find_cubes, object_type=cozmo.objects.LightCube, timeout=1000)
    except TimeoutError:
        print("not found")
        return
    finally:

        for j in range(len(cubes)-1,0,-1):
            for i in range(j):
                if cubes[i].pose.position.y > cubes[i+1].pose.position.y:
                    temp = cubes[i]
                    cubes[i] = cubes[i + 1]
                    cubes[i + 1] = temp
        for cube in cubes:
            cube.set_lights(cozmo.lights.Light(cozmo.lights.Color(int_color=0xff000000)))
            cubeObjectIds.append(cube.object_id);
        if(find_cubes == len(cubes)):
            await blinkCubes(coz_conn=coz_conn, cubes=cubes)
            for cube in cubes:
                cube.set_lights_off();
        else:
            print("not found")

async def moveForward():
    global takeInput;
    global foundWinner;
    global sentResponseToServer;

    await coz.set_lift_height(0, accel=50.0).wait_for_completed()
    
    if foundWinner is False:
        await coz.drive_wheels(50, 50, duration=3)
        await sendPlayerReachedMic();
        sentResponseToServer = False;
        takeInput = True;

async def moveBack():
    global foundWinner;
    if foundWinner is False:
        await coz.drive_wheels(-50, -50, duration=3)

async def sayword(word):
    await coz.say_text(word, voice_pitch=voice_pitch, duration_scalar=1.5).wait_for_completed()

async def run(coz_conn):

    asyncio.set_event_loop(coz_conn._loop);
    global coz;
    coz = await coz_conn.wait_for_robot()

    await coz.set_head_angle(degrees(5.0), accel=50.0).wait_for_completed()
    await coz.set_lift_height(0, accel=50.0).wait_for_completed()

    await startWorld(coz, coz_conn)

    await connectToServer();

    asyncio.ensure_future(pollActivePlayer());
    asyncio.ensure_future(pollWinner());

    coz.world.add_event_handler(cozmo.objects.EvtObjectTapped, on_object_tapped)

    # await coz.drive_wheels(50, 50, 50, 50, duration=3)
    # await coz.turn_in_place(degrees(45)).wait_for_completed()
    # await asyncio.sleep(2);
    # await coz.say_text("superb").wait_for_completed()
    # await asyncio.sleep(2);
    # await coz.turn_in_place(degrees(-45)).wait_for_completed()
    # await coz.drive_wheels(-50, -50, -50, -50, duration=3)
    # await coz.say_text("Bye! Have a good day").wait_for_completed()

    await asyncio.sleep(100000000);

    # coz.pickup_object(cubes[0]).wait_for_completed()
    # coz.place_on_object(cubes[1]).wait_for_completed()




    # coz.set_lift_height(0.0).wait_for_completed()

    # coz.set_head_angle(degrees(-20.0),accel=50.0).wait_for_completed()
    # coz.set_head_angle(degrees(20.0),accel=50.0).wait_for_completed()
    # coz.set_head_angle(degrees(-20.0),accel=50.0).wait_for_completed()
    # coz.set_head_angle(degrees(20.0),accel=50.0).wait_for_completed()

    # coz.move_lift(0.15)
    # coz.move_head(0.15)

async def on_object_tapped(event,	*,	obj,	tap_count,	tap_duration,	**kw):
    print("Received	a	tap	event", event)
    # if event.tap_intensity < 85:
    #     return;
    global waitingBool
    global userLetter
    global userWord
    global currentLetterLength;

    if waitingBool or takeInput is False:
        return

    waitingBool = True
    repeatPressed = False;

    if cubeObjectIds.index(obj.object_id) == 0:
        cubes[0].set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[0])))
        userLetter += '.'
        currentLetterLength = len(userLetter)
        thisletterlength = currentLetterLength
    elif cubeObjectIds.index(obj.object_id) == 2:
        cubes[2].set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[1])))
        userLetter += '-'
        currentLetterLength = len(userLetter)
        thisletterlength = currentLetterLength
    elif cubeObjectIds.index(obj.object_id) == 1:
        cubes[1].set_lights(cozmo.lights.Light(cozmo.lights.Color(colors[2])))
        repeatPressed = True;
        # await sayword(currentWord)
        await sendRepeatRequest();

    await asyncio.sleep(0.2)
    await switchofflights()

    waitingBool = False;

    await asyncio.sleep(2)

    if repeatPressed is False and currentLetterLength == thisletterlength:
        if userLetter in morseCodes:
            index = morseCodes.index(userLetter);
            character = chr(index+65)
            userWord += character
            userLetter = ''
            await sayword(character)
            await checkWord();
        else:
            userWord += '.';
            await checkWord();

    # global ismyturnactive;
    # ismyturnactive = False;
    # await SendPlayerAnser();

async def checkWord():
    global userWord
    global currentWord
    global userWord
    global userLetter
    global takeInput;
    global speakWord;
    global type;

    isCorrect = True;
    for i in range(0,len(userWord)):
        if currentWord[i] != userWord[i]:
            isCorrect = False;

    if isCorrect:
        if len(userWord) == len(currentWord):
            takeInput = False;
            for cube in cubes:
                cube.set_lights(cozmo.lights.Light(cozmo.lights.Color(0x00ff0000)))

            await sayword(speakWord);

            await SendPlayerAnswer();

            await coz.play_anim_trigger(HappyTriggers[random.randrange(0,len(HappyTriggers))]).wait_for_completed();
            await switchofflights();
            await moveBack();
    else:
        userWord = ''
        userLetter = ''
        takeInput = False;
        for cube in cubes:
            cube.set_lights(cozmo.lights.Light(cozmo.lights.Color(0xff000000)))
        await SendPlayerIncorrect(False);

        await coz.play_anim_trigger(SadTriggers[random.randrange(0,len(SadTriggers))]).wait_for_completed();

        await asyncio.sleep(1);
        # await sayword("Incorrect");
        await switchofflights();
        if type != 'Tutorial':
            await moveBack();
        else:
            takeInput = True;


async def switchofflights():
    for cube in cubes:
        cube.set_lights_off();

async def newword(word_from_server, question_type, speak_word):
    global currentWord;
    global userWord;
    global userLetter;
    global type;
    global speakWord;

    userWord = ''
    userLetter = ''
    currentWord = word_from_server;
    type = question_type;
    speakWord = speak_word;
    await moveForward();

async def connectToServer():
    global conn;
    global currentPlayerNumber;

    conn = http.client.HTTPConnection(server_ip);
    dict = {'playername': str(currentPlayerName)}
    params = json.dumps(dict);
    # params = '{"playername":"' + str(currentPlayerName) + '"}';
    headers = {"Content-type": "application/json"}
    conn.request("POST", "/connectToGame", params, headers)
    response = conn.getresponse()
    data = response.read()
    decodedData = data.decode('UTF-8')
    datadict = ast.literal_eval(decodedData);
    currentPlayerNumber = datadict['playerNum'];
    conn.close();

async def pollActivePlayer():
    global ismyturnactive;
    global pollfortimer;

    while foundWinner is False:
        conn.request("GET", "/getCurrentPlayer")
        response = conn.getresponse()
        data = response.read()
        decodedData = data.decode('UTF-8')
        datadict = ast.literal_eval(decodedData);
        activePlayer = datadict['activePlayer'];
        if activePlayer == currentPlayerNumber and ismyturnactive is False:
            ismyturnactive = True;
            await newword(datadict['word'],datadict['type'],datadict['sayword']);
        await asyncio.sleep(1);
        conn.close();

async def sendPlayerReachedMic():
    dict = {'playerNum': str(currentPlayerNumber)}
    params = json.dumps(dict);
    headers = {"Content-type": "application/json"}
    conn.request("POST", "/reachedMic", params, headers)
    response = conn.getresponse()
    conn.close();

async def sendRepeatRequest():
    dict = {'playerNum': str(currentPlayerNumber)}
    params = json.dumps(dict);
    headers = {"Content-type": "application/json"}
    conn.request("POST", "/repeatRequest", params, headers)
    response = conn.getresponse()
    conn.close();

async def SendPlayerIncorrect(timeUp):
    global currentPlayerNumber;
    global ismyturnactive;
    global sentResponseToServer;

    if sentResponseToServer is False:
        sentResponseToServer = True;
        dict = {'playerNum': str(currentPlayerNumber),
                'timeUp': str(timeUp)
                }
        params = json.dumps(dict);
        headers = {"Content-type": "application/json"}
        conn.request("POST", "/incorrectAnswer", params, headers)
        response = conn.getresponse()
        conn.close();

        if type != 'Tutorial':
            ismyturnactive = False;
        else:
            sentResponseToServer = False;
    else:
        print("COULD NOT SEND SHIT");

async def SendPlayerAnswer():
    global currentPlayerNumber;
    global ismyturnactive;
    global sentResponseToServer;

    if sentResponseToServer is False:
        sentResponseToServer = True;
        dict = {'playerNum': str(currentPlayerNumber) , 'userAnswer':userWord }
        params = json.dumps(dict);
        # params = '{"playerNum":"' + str(currentPlayerNumber) + '","userAnswer":"' + userWord + '"}';
        headers = {"Content-type": "application/json"}
        conn.request("POST", "/userAnswer", params, headers)
        response = conn.getresponse()
        conn.close();

        ismyturnactive = False;

    # data = response.read()
    # decodedData = data.decode('UTF-8')
    # datadict = ast.literal_eval(decodedData);
    # print(datadict);


async def pollWinner():

    global currentPlayerNumber;
    global foundWinner;
    global takeInput;

    while foundWinner is False:
        conn.request("GET", "/getWinner")
        response = conn.getresponse()
        data = response.read()
        decodedData = data.decode('UTF-8')
        datadict = ast.literal_eval(decodedData);
        serverWinner = int(datadict['winner']);
        if serverWinner != 0:
            foundWinner = True;
            takeInput = False;
            if serverWinner == currentPlayerNumber:
                await playWinAnimation()
            # else:
            #     await playLoseAnimation()
        await asyncio.sleep(1);
        conn.close();

async def playWinAnimation():
    while True:
        await coz.play_anim_trigger(WinAnimationTrigger).wait_for_completed();
        await asyncio.sleep(0.5);

async def playLoseAnimation():
    while True:
        await coz.play_anim_trigger(LoseAnimationTrigger).wait_for_completed();
        await asyncio.sleep(0.5);


class test():
    def __init__(self, master=None):
        self.entry = None;
        self.render();

    def render(self):
        self.root = Tk()

        label = ttk.Label(self.root,text = 'Annual Cozmo Spelling Bee') #creates label object but not displayed yet
        label.pack() #Displays text
        label = ttk.Label(self.root,text = 'Enter Name') #creates label object but not displayed yet
        label.pack() #Displays text

        self.entry = ttk.Entry(self.root, width = 30)
        self.entry.pack()

        label = ttk.Label(self.root, text='Enter IP')  # creates label object but not displayed yet
        label.pack()  # Displays text

        self.serverentry = ttk.Entry(self.root, width=30)
        self.serverentry.insert(0,server_ip);
        self.serverentry.pack()

        button = ttk.Button(self.root, text= 'Enter', command=self.ButtonPressed)
        button.pack()
        button['text']
        'Enter'

        self.root.mainloop();

    def ButtonPressed(self):
        global currentPlayerName;
        global server_ip;

        currentPlayerName = self.entry.get();
        server_ip = self.serverentry.get();

        self.root.destroy();
        cozmo.setup_basic_logging()
        cozmo.connect_with_tkviewer(run)
        # cozmo.connect(run)

app = test();

#
# if __name__ == '__main__':
#     cozmo.setup_basic_logging()
#     cozmo.connect_with_tkviewer(run)
