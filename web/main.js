(function init() {
  var jImageEl = $('.image-container');
  var playersEl = $('.players-text');
  var currentEL = $('.current-text');
  var livesEL = $('.lives-text');
  var credits = $('.credits-text');
  credits.hide();
  var timerTime = 60;
  var currentTime = 0;
  var stopTimerBool = false;
  var type = '';
  var gotWinner = false;
  var playerNames = [];

  window.setInterval(function(){ 
	  $.get('http://localhost:5000/getCurrentPlayer', function(path) {
	  		myObject = JSON.parse(path);
	  		currentPlayer = myObject['playerName'];
	  		type = myObject['type'];
	  		if(type == 'Timer') {
	  			timerTime = parseInt(myObject['time']);
	  		}
	  		if(currentPlayer != null && gotWinner == false) {
	  			var str = '<h1 style="color:#9AD4D6;">' + currentPlayer.toString() + "'s Turn</h1>";
	  			if(myObject['type'].toString() == "Reverse") {
	  				str = str + '<h1>Spell the word backwards</h1>';
	  			} else if(myObject['type'].toString() == "NoVowel") {
	  				str = str + '<h1>Spell the word without any vowels</h1>';
	  			} else if(myObject['type'].toString() == "Normal") {
	  				str = str + '<h1>Spell the word</h1>';
	  			} else if(myObject['type'].toString() == "Tutorial") {
	  				str = str + '<h1>Practice</h1>';
	  			}

	      		currentEL.html(str);
	      		playersEl.hide();
	      	}
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 500);

  window.setInterval(function(){ 
	  $.get('http://localhost:5000/shouldSayWordWeb', function(path) {
	  		myObject = JSON.parse(path);
	  		sayword = myObject['word'];
	  		newword = myObject['newWord'];

	  		// sayword = "1";

	  		if(newword == "true" && gotWinner == false) {
	      		// jImageEl.html('<img src="./images/' + sayword + '.jpg"/>');
	      		currentTime = timerTime;
	      		stopTimerBool = false;
	      		
	      		if(type == "Timer") {
	      			startTimer();
	      		}
	      		
	      		jImageEl.css('background-image','url("/images/' + sayword + '.jpg")');
	      	}
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 500);

  window.setInterval(function(){ 
	  $.get('http://localhost:5000/incorrectCount', function(path) {
	  		myObject = JSON.parse(path);
	  		incorrectCounts = myObject['incorrectCount'].toString();
	  		incorrectAnswers = incorrectCounts.split(",");
	  		if(incorrectCounts == "") {
	  			incorrectAnswers = [];
	  		}
	  		str = '<h1>Lives<br>'
	  		for(var i = 0 ; i < incorrectAnswers.length ; i++) {
	  			str = str + playerNames[i] + ":";
	  			console.log(incorrectAnswers[i]);
	  			if(incorrectAnswers[i] == 0) {
	  				str += "3";
	  			} else if(incorrectAnswers[i] == 1) {
	  				str += "2";
	  			} else if(incorrectAnswers[i] == 2) {
	  				str += "1";
	  			} else if(incorrectAnswers[i] >= 3) {
	  				str += "0";
	  			}
	  			str += "<br>";
	  		}
	  		str += '</h1>'
	  		livesEL.html(str);
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 200);

  window.setInterval(function(){ 
	  $.get('http://localhost:5000/doStopTimer', function(path) {
	  		myObject = JSON.parse(path);
	  		stopTimer = myObject['stopTimer'];

	  		if(stopTimer == "true") {
	      		// jImageEl.html('<img src="./images/' + sayword + '.jpg"/>');
	      		stopTimerBool = true;
	      	}
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 200);

  function startTimer() {
	str = "00:" + currentTime.toString();
	timerEL.html('<h1>' + str + '</h1>');
	currentTime -= 1;
	if(currentTime >= 0 && stopTimerBool == false) {
  		window.setTimeout(startTimer,1000);
  	} else if(stopTimerBool == false) {
  		timerEL.html('<h1>00:00</h1>');
  		$.post( "http://localhost:5000/timerEnd", function( data ) {
		});
  	}

  }

  window.setInterval(function(){ 
	  $.get('http://localhost:5000/getWinner', function(path) {
	  		myObject = JSON.parse(path);
	  		var winner = parseInt(myObject['winner']);
	  		if(playerNames.length >= winner) {
		  		var winnerName = playerNames[winner-1];
		  		if(winner > 0) {
		  			gotWinner = true;
		  			jImageEl.hide();
		  			playersEl.hide();
		  			livesEL.hide();
		  			credits.show();
		  			var str = '<h1><b>' + winnerName.toString() + ' Wins! </b></h1>';
			  		currentEL.html(str);
			  		currentEL.css({
					    fontSize: 20
					});
		  		}
		  	}
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 500);

  window.setInterval(function(){ 
	  $.get('http://localhost:5000/getPlayers', function(path) {
	  		myObject = JSON.parse(path);
	  		players = myObject['players'].split(",");
	  		if(myObject['players'] == ""){
	  			players = [];
	  		}
	  		playerNames = players;

	  		var str = '<h2>';
	  		for(var i = 0 ; i < players.length ; i++) {
	  			str = str + players[i] + ",";
	  		}
	  		str = str.substr(0,str.length-1)
	  		str += '</h2>';
	  		if(players.length != 0) {
	  			playersEl.html(str);
	  		}
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 500);

  // setTimeout(function(){ 
	 //  $.get('/api/imageUrl', function() {
	 //      jImageEl.html('<img src="./images/' + path + '"/>');
	 //    })
	 //    .fail(function() {
	 //      console.log('Sorry failed to load an image.');
	 //    });
  // }, 5000);

  // setTimeout(function(){ 
	 //  $.get('/api/imageUrl', function() {
	 //      jImageEl.html('<img src="./images/' + path + '"/>');
	 //    })
	 //    .fail(function() {
	 //      console.log('Sorry failed to load an image.');
	 //    });
  // }, 5000);

})();