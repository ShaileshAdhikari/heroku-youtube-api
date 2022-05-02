
function get_data() {
    let base_url = window.location.origin;
    $.getJSON(base_url + '/get-song-list', function (data) {
        console.log(data);
        if (data.result.songList){
            let song_list = data.result.songList;
            let playing = data.result.playing;
            let most_played = data.result.mostPlayed;
            var song_list_html = '';
            var most_played_html = '';
            var playing_html = '';

            if (song_list.length > 0) {
                for (let i = 0; i < song_list.length; i++) {
                    song_list_html += '<div class="media d-flex">' +
                        '<div style="height: 100px">' +
                        '<a href="#"> <img class="media-object h-100" src='+song_list[i].thumbnail+' alt="..."> </a>' +
                        '</div><div class="px-2" style="color: white;">' +
                        '<h6 style="line-height: 1.25rem;" >'+ song_list[i].name +'</h6>' +
                        '<p class="m-0 p-0"> '+ song_list[i].duration +'</p>' +
                        '<p class="m-0 p-0"> Added By: '+ song_list[i].added_by +'</p>' +
                        '</div></div>'
                }
            }
            else{
                song_list_html = '<div class="text-bolder text-lg-center"> Add Songs !</div>'
            }

            if (playing.length > 0) {
                    playing_html += '<div class="col-lg-4 mt-2 mt-lg-0">'+
                        '<div class="position-relative d-flex align-items-center justify-content-center">'+
                        '<img class="w-100 position-relative z-index-2 pt-4" src='+ playing[0].thumbnail +'>'+
                        '</div></div><div class="col-lg-8" >'+
                        '<div class="d-flex flex-column h-100">'+
                        '<p class="mb-1 pt-1 text-bolder">Currently Playing</p>'+
                        '<h6 class="font-weight-bold">'+ playing[0].name +'</h6>'+
                        '<p class="m-0">Duration : '+ playing[0].duration +'</p>'+
                        '<p class="m-0"> Added by: '+ playing[0].added_by +'</p>'+
                        '</div></div>'
            }
            else{
                playing_html = '<div class="text-bolder text-lg-center"> No Songs Playing !</div>'
            }

            if (most_played.length > 0) {
                    most_played_html += '<div class="col-lg-4 mt-2 mt-lg-0">'+
                        '<div class="position-relative d-flex align-items-center justify-content-center">'+
                        '<img class="w-100 position-relative z-index-2 pt-4" src='+ most_played[0].thumbnail +'>'+
                        '</div></div><div class="col-lg-8" >'+
                        '<div class="d-flex flex-column h-100">'+
                        '<p class="mb-1 pt-1 text-bolder">Most Played</p>'+
                        '<h6 class="font-weight-bold">'+ most_played[0].name +'</h6>'+
                        '<p class="m-0">Duration : '+ most_played[0].duration +'</p>'+
                        '<p class="m-0"> Added by: '+ most_played[0].added_by +'</p>'+
                        '</div></div>'
            }
            else{
                most_played_html = '<div class="text-bolder text-lg-center"> No Most Played !</div>'
            }

        }
            document.getElementById('playlistId').innerHTML = song_list_html;
            document.getElementById('playingId').innerHTML = playing_html;
            document.getElementById('mostplayedId').innerHTML = most_played_html;
        });
}