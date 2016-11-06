var express = require('express');
var bodyParser = require('body-parser');

var app = express();

types = ['Tutorial','Normal','Reverse','NoVowels']
words = [];

function shuffle(a) {
    var j, x, i;
    for (i = a.length; i; i--) {
        j = Math.floor(Math.random() * i);
        x = a[i - 1];
        a[i - 1] = a[j];
        a[j] = x;
    }
}

fs = require('fs')
fs.readFile('./words.txt', 'utf8', function (err,data) {
  if (err) {
    return console.log(err);
  }
  lines = data.split(/\r?\n/)
  for(var i = 0 ; i < lines.length ; i++) {
  	eachRow = lines[i].split(",");
  	shuffle(eachRow);
  	words.push(eachRow);
  }
  console.log(words);
});

var difficultyCounts = [1,2];
var currentCount = 0;

var lastReverseWordIndex = -1;
var lastNoVowelWordIndex = -1;

var rightAnswerTexts = ["I guess that one was too easy for you.",
"Maybe you just got lucky.",
"You must be a genius.",
"Have you done this before? You're an expert.",
"Bingo. You nailed it.",
"I'm a robot, and even I didn't know that one.",
"You should consider being an english teacher.",
"Correct.",
"That was perfect.",
"Next time, don't think so hard. You're sweating!",
"You got it.",
"Fantastic.",
"They should call you Doctor A B C.",
"Next time I'll give you something harder.",
"Perfect spelling.",
"Have you done this before?",
"You must read the dictionary all day.",
"I wish my kids took spelling as seriously as you do."];

var wrongAnswerTexts = ["Better luck next time. You'll need it.",
"We better call the school janitor, because that word mopped the floor with you.",
"There's always next time.",
"Incorrect.",
"Oops. Try again next time.",
"I spelled better than you when I was only a a floppy disk.",
"Spelling isn't for everyone.",
"Maybe you'll get an easier word next time.",
"Are you distracted? You must be distracted.",
"Your brain must have crossed wires. I should know. I'm a robot.",
"You can't take things back in the serious game of spelling.",
"Swing and a miss.",
"Nice try, but not nice enough.",
"Have you ever tried math? Maybe you're better at that.",
"At least you can spell your name probably.",
"Sorry.",
"You probably wish that didn't happen."];

var maxPlayers = 2;

var incorrectAnswers = [];
var players = [];
var losers = [];
var currentPlayer = 0;
var winner = 0;
var currentWordIndex = 0;
var currenttype = 0;
var judgeSayWord = '';
var judgeSayWordWeb = '';

var timeUp = false;
var time = 50;
var stopTimer = false;

var foundWinner = false;

var maxLives = 3;

var newWord = false;
var newWordWeb = false;

app.set('port', (process.env.PORT || 5000));

app.use(bodyParser.json());
app.use(express.static(__dirname + '/public'));

// views is directory for all template files
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');

app.get('/', function(request, response) {
  response.send('Hello world');
});

app.get('/getPlayers', function(request, response) {
	var obj = {
  	'players':players.toString()
	};
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  response.send(JSON.stringify(obj));
});

app.get('/getCurrentPlayer', function(request, response) {
	inputWord = words[currenttype][currentWordIndex].toString();
	if(currenttype == 2) {
		inputWord = inputWord.split("").reverse().join("")
	} else if(currenttype == 3) {
		arr = inputWord.split("");
		newarr = [];
		for(var i = 0 ; i < arr.length ; i++) {
			if(arr[i] != 'A' && arr[i] != 'E' && arr[i] != 'I' && arr[i] != 'O' && arr[i] != 'U' ) {
				newarr.push(arr[i]);
			}
		}
		inputWord = newarr.join("");
	}
  var obj = {
  	'activePlayer': currentPlayer.toString(),
  	'playerName': players[currentPlayer-1],
  	'word':inputWord,
  	'type':types[currenttype].toString(),
  	'sayword':words[currenttype][currentWordIndex].toString(),
  	'time':time.toString()
	};
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');

  response.send(JSON.stringify(obj));
});

app.post('/startGame', function(req, res){
	players = [];
	losers = [];
	currentPlayer = 0;
	winner = 0;
	currentWordIndex = 0;
	incorrectAnswers = [];
	judgeSayWord = '';
	judgeSayWordWeb = ''
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.post('/timerEnd', function(req, res){
	console.log("TIME IS UP");
	timeUp = true;
	timeUpJudge = true;
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.get('/doStopTimer', function(request, response) {
  var obj = {
  	'stopTimer': stopTimer.toString(),
	};
	stopTimer = false;
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.get('/isTimeUp', function(request, response) {
  var obj = {
  	'timeUp': timeUp.toString(),
	};
	timeUp = false;
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.get('/isTimeUpJudge', function(request, response) {
  var obj = {
  	'timeUp': timeUpJudge.toString(),
	};
	timeUpJudge = false;
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.get('/shouldSayWordWeb', function(request, response) {
  var obj = {
  	'word': judgeSayWordWeb.toString(),
  	'newWord':newWordWeb.toString()
	};
	judgeSayWordWeb = '';
	newWordWeb = false;
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.get('/shouldSayWord', function(request, response) {
  var obj = {
  	'word': judgeSayWord.toString(),
  	'newWord':newWord.toString()
	};

	if( judgeSayWord != '') {
		console.log(judgeSayWord);
	}
	judgeSayWord = '';
	newWord = false;
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.post('/connectToGame', function(req, res){
	players.push(req.body.playername);
	incorrectAnswers.push(0);

	console.log(req.body.playername);
	var playerNum = players.length;
	var tosend = '{"playerNum":"' + playerNum.toString() + '"}';
	var obj = {
  	'playerNum': playerNum.toString()
  	};
	if(players.length == maxPlayers) {
		currentPlayer = 1;
	}
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(JSON.stringify(obj));
});

app.get('/incorrectCount', function(request, response) {
  var obj = {
  	'incorrectCount': incorrectAnswers.toString(),
	};
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.get('/getWinner', function(request, response) {
  var obj = {
  	'winner': winner.toString(),
	};
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.post('/reachedMic', function(req, res){
	console.log("reached mic");
	playerIndex = req.body.playerNum;
	if(playerIndex == currentPlayer) {
		console.log("is same player");
		judgeSayWord = words[currenttype][currentWordIndex].toString();
		judgeSayWordWeb = words[currenttype][currentWordIndex].toString();
		newWord = true;
		newWordWeb = true;
	}
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.post('/repeatRequest', function(req, res){
	playerIndex = req.body.playerNum;
	if(playerIndex == currentPlayer && foundWinner == false) {
		judgeSayWord = words[currenttype][currentWordIndex].toString();
	}
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.post('/userAnswer', function(req, res){
	userInput = req.body.userAnswer;
	playernumber = req.body.playerNum;
	console.log(playernumber + "," + userInput);
	currentPlayer += 1;
	
	stopTimer = true;
	judgeSayWord = rightAnswerTexts[Math.floor(Math.random()*rightAnswerTexts.length)];
	if(currentPlayer > players.length) {
		currentCount++;
		if(currenttype < 2) {
			if(currentCount >= difficultyCounts[currenttype]) {
				currenttype++;
				currentCount = 0;
				currentWordIndex = -1;
			}
		} else {
			if(Math.random() < 0.5) {
				currenttype = 2;
				currentWordIndex = lastReverseWordIndex;
			} else {
				currenttype = 3;
				currentWordIndex = lastNoVowelWordIndex;
			}
		}
		currentPlayer = 1;
	}
	currentWordIndex++;
	if(currenttype == 2) {
		lastReverseWordIndex = currentWordIndex;
	} else if(currenttype == 3) {
		lastNoVowelWordIndex = currentWordIndex;
	}
	if(currentWordIndex >= words[currenttype].length) {
		currentWordIndex = 0;
	}
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.post('/incorrectAnswer', function(req, res){
	playerIndex = req.body.playerNum - 1;
	
	if(currenttype != 0) {
		incorrectAnswers[playerIndex] += 1;
	
		if(incorrectAnswers[playerIndex] >= maxLives) {
			losers.push(playerIndex);
		}

		if(req.body.timeUp == "False") {
			stopTimer = true;
			judgeSayWord = wrongAnswerTexts[Math.floor(Math.random()*wrongAnswerTexts.length)];
		}
	} else {
		judgeSayWord = wrongAnswerTexts[Math.floor(Math.random()*wrongAnswerTexts.length)];
	}

	if(players.length > 1) {
		if(losers.length == players.length-1) {
			for (i = 0; i < players.length; i++) { 
			    if(losers.indexOf(i) == -1) {
			    	winner = (i+1);
			    	foundWinner = true;
			    	currentPlayer = 0;
			    }
			}
		}
	}

	if(foundWinner == false && currenttype != 0) {
		currentPlayer += 1;
		if(currentPlayer > players.length) {
			currentCount++;
			if(currenttype < 2) {
				if(currentCount >= difficultyCounts[currenttype]) {
					currentCount = 0;
					currenttype++;
					currentWordIndex = -1;
				}
			} else {
				if(Math.random() < 0.5) {
					currenttype = 2;
					currentWordIndex = lastReverseWordIndex;
				} else {
					currenttype = 3;
					currentWordIndex = lastNoVowelWordIndex;
				}
			}
			currentPlayer = 1;
		}
		currentWordIndex++;
		if(currenttype == 2) {
			lastReverseWordIndex = currentWordIndex;
		} else if(currenttype == 3) {
			lastNoVowelWordIndex = currentWordIndex;
		}
		if(currentWordIndex >= words[currenttype].length) {
			currentWordIndex = 0;
		}
	}
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.listen(app.get('port'), function() {
  console.log('Node app is running on port', app.get('port'));
});