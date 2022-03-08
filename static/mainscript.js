// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');
tag.id = 'iframe'
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
var player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('existing-iframe', {
        height: '315',
        width: '560',
        videoId:'icPHcK_cCF4',
        playerVars: {
            autoplay: 1,
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    document.getElementById('existing-iframe').style.borderColor = '#FF6D00';
    console.log('Player Started',player)
}

function stopVideo() {
    player.stopVideo();
}

function playVideo() {
    player.playVideo();
}

function loadVideo(play) {
    player.loadVideoById(play);
}

function changeBorderColor(playerStatus) {
    var color;
    if (playerStatus == -1) {
        color = "#37474F"; // unstarted = gray
    } else if (playerStatus == 0) {
        color = "#FFFF00"; // ended = yellow
    } else if (playerStatus == 1) {
        color = "#33691E"; // playing = green
    } else if (playerStatus == 2) {
        color = "#DD2C00"; // paused = red
    } else if (playerStatus == 3) {
        color = "#AA00FF"; // buffering = purple
    } else if (playerStatus == 5) {
        color = "#FF6DOO"; // video cued = orange
    }
    if (color) {
        document.getElementById('existing-iframe').style.borderColor = color;
    }
}

// 5. The API calls this function when the player's state changes.
function onPlayerStateChange(event) {
    console.log("state Changed", event)
    changeBorderColor(event.data);
    if (event.data == YT.PlayerState.ENDED) {
        console.log("PLAYER ENDED")
        $.post("/end", function (res, status){
            console.log(res)
            if (res.length > 15){
                $( "h1#remarks-h1" ).html( "Remarks: " + res );
                player.playVideo()
            }else {
                $( "h1#remarks-h1" ).html( "Remarks: SUCCESSFUL" );
                player.loadVideoById(res)
            }
        })
    }
}

// Volume Control
function VolumeUp() {
    player.setVolume(player.getVolume() + 5);
    document.getElementById('volume-meter').value = player.getVolume();
}

function VolumeDown() {
    player.setVolume(player.getVolume() - 5);
    document.getElementById('volume-meter').value = player.getVolume();
}
