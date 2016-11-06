/**
 * Created by sharan on 27/10/15.
 */

var creds = new AWS.CognitoIdentityCredentials( {
  IdentityPoolId: 'ap-northeast-1:e815b597-f74a-44c3-8e65-f636205aa47c',
} );
AWS.config.credentials = creds;
AWS.config.region = 'ap-northeast-1';
var db = new AWS.DynamoDB( { dynamoDbCrc32: false } );

function addDataToDB(name, email, phone, message) {
    var id = ""+Date.now()+name;
    var params = {
        TableName:'SSContactForm',
        Item:{
            "rowID": {
              S: id
            },
            "name": {
              S: name
            },
            "email": {
              S: email
            },
            "phone": {
              S: phone
            },
            "message": {
              S: message
            }
        }
    };

    db.putItem(params, function(err, data) {
        if (err) {
            // console.error("Unable to add item. Error JSON:", JSON.stringify(err, null, 2));
        } else {
            // console.log("Added item:", JSON.stringify(data, null, 2));
        }
    });
}

function onLoadPage(){
    startSlider();
    $(document).ready(function() {
        $(".portfolio-thumb").click(function() {
             // startSlider();
        });
    });
}

function startSlider(){
    // $(".project-slider").brazzersCarousel();
    
    $(".project-slider").owlCarousel({
 
      navigation : true, // Show next and prev buttons
      slideSpeed : 300,
      paginationSpeed : 400,
      singleItem:true,
      autoPlay: 3000,
      stopOnHover: true
  });
    // $('.project-slider').slick({
    //     adaptiveHeight:false,
    //     autoplay: true,
    //     dots:true,
    //     edgeFriction:0.1,
    //     lazyLoad: 'progressive',
    //     pauseOnHover:true,
    //     arrows:true,
    //     infinite: true,
    //     speed: 500,
    //     fade: true,
    //     cssEase: 'linear'
    // });
}

function sendContactEmail(name, email, number, message){
    addDataToDB(name,email,number,message);

    var dataToSend = {};
    dataToSend.name = name;
    dataToSend.email = email;
    dataToSend.number = number;
    dataToSend.message = message;

    $.ajax({
        type: 'POST',
        data: JSON.stringify(dataToSend),
        contentType: 'application/json',
                url: '/contact',     
                success: function(data) {
                    // console.log('success');
                    // console.log(JSON.stringify(data));
                }
            });
}