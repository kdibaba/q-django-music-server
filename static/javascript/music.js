// GLOBAL CONSTANTS

CURRENT_ALBUM = ''
PLAYLIST = ''
NOW_PLAYING = false
// AJAX CALLS
function get_all_artists() {
	$.get("/artists/", function(jsonArtists) {
		show_artists(jsonArtists);
	});
};

function show_artists(jsonArtists) {
	var artists = jQuery.parseJSON(jsonArtists);
	var artist_count = 0

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="artists"></div>');
	$('#artists').append('<ul>');
	$.each(artists, function(i,item){
		artist_count+=1;
		$('#artists').append('<div onclick="get_albums_by_artist('+item.pk+')"><text class="artist_name" >' + item.fields.artist + '</text></div>');
	})
	$('#artists').append('</ul>');
	$('#artists').prepend('<p class="nav_header">' + artist_count + ' Artists</p>');
}

function get_all_albums() {
	jQuery.ajax({
		url: "/albums/", 
		success: function(jsonAlbums) {show_albums(jsonAlbums)},
		async	: false
	});
};

function show_albums(jsonAlbums) {
	var albums = jQuery.parseJSON(jsonAlbums);
	var album_count = 0
	var cover_count = 0;
	var missing_cover_count = 0;

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="albums"></div>');
	$.each(albums, function(i,item){
		album_count+=1;
		$('#albums').append('<div class="album album_' + item.pk + '" onclick="get_album_show('+item.pk+')">' + '<h1 class="album_name">' + item.fields.album + '</h1>' + '</div>');
		$('.album_' + item.pk).append('<text>' + item.fields.song_count + ' SONGS</text>')
		if (item.fields.album_art){
			//cover_count += 1;
			$('.album_'+item.pk).prepend( '<div id="img_div"><img src="/static/music/'+ item.fields.letter +'/' + item.fields.folder + '/Folder.jpg' + '" /></div>' )}
		else {
			//missing_cover_count += 1
			;$('.album_'+item.pk).prepend( '<div id="img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
	})
	$('#albums').prepend('<p class="nav_header">' + album_count + ' Albums</p>');
	//alert('Cover Count = ' + cover_count);
	//alert('Missing Cover Count = ' + missing_cover_count);
}

function get_albums_by_artist(artist_id) {
	$.get("/albums/" + artist_id + "/", function(jsonAlbums) {
	        show_albums(jsonAlbums);
	});
};

function get_album_show(album_id) {
	jQuery.ajax({
		url: "/album/" + album_id + "/", 
		success: function(jsonAlbum) {show_album(jsonAlbum, 1);},
		async	: false
	});
};

function get_album_play(album_id) {
	jQuery.ajax({
		url: "/album/" + album_id + "/", 
		success: function(jsonAlbum) {play_album(jsonAlbum, 2);},
		async	: true
	});
};

function get_album_info(album_id) {
	jQuery.ajax({
		url: "/album_info/" + album_id + "/",
		success: function(jsonAlbumInfo){CURRENT_ALBUM = jQuery.parseJSON(jsonAlbumInfo);},
		async:   false
	});
};

function show_album(jsonAlbum, show_or_play) {
	var album = jQuery.parseJSON(jsonAlbum);

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="album"></div>');
	get_album_info(album[0].fields.album);
	
	$('#album').append('<div class="current_album"></div>')
	$.each(CURRENT_ALBUM, function(i,item){
		if (item.fields.album_art){$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/music/' +item.fields.letter+ '/' + item.fields.folder + '/Folder.jpg' + '" /></div>' )}
		else {$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
		$('.current_album').append( '<button id="play_album_button" onclick="get_album_play('+item.pk+')">PLAY ALBUM</button>')
	})
	CURRENT_ALBUM = ''
	
	$('#album').append('<table id="song_table"><tr><th>Title</th><th>Length</th><th>Rating</th></tr></table>')
	$.each(album, function(i,item){
		if (item.fields.type == 'mp3'){
			$('#song_table').append('<tr class="songs" id="song_'+item.pk+'" ><td ondblclick="play_song(\''+item.pk+'\', \'' + item.fields.type + '\', \'' + item.fields.letter + '\', \'' + item.fields.path + '\', \'' + item.fields.filename + '\')">' + item.fields.title + '</td>' +
			'<td>' + item.fields.length + '</td>' + '<td>' + item.fields.rating + '</td>');
		}
	})
	$('#albums').append('</table>');
	if (show_or_play == 2){play_album(jsonAlbum)}
}

function play_song(song_id, type, letter, path, song) {
	$('.songs').css('background', '#F7F7F7').css('color', '#555555')
	$('#song_' + song_id).css('background', '#7FAD35').css('color', '#ffffff')
	
	//If playlist is being displayed when someone wants to play a single song,
	//Hide the playlist.
	if (PLAYLIST){hide_playlist()}
	var destiny = "/static/music/"+letter+"/"+path+"/"+song;
	
	recreate_playlist();
	PLAYLIST = new jPlayerPlaylist({
		jPlayer: "#jquery_jplayer_1",
		cssSelectorAncestor: "#jp_container_1"
	},  [], {
		swfPath: "/static/javascript/",
		supplied: "oga, mp3",
		solution: "html, flash"
	});	
	
	$("#jquery_jplayer_1").jPlayer("setMedia", {
		'mp3': destiny,
	}).jPlayer("play");
	NOW_PLAYING = true
}

function play_album(jsonAlbum){
	$('.songs').css('background', '#F7F7F7').css('color', '#555555')
	var album = jQuery.parseJSON(jsonAlbum);
	recreate_playlist();
	var album_songs = []
	$.each(album, function(i,item){
		if (item.fields.type == 'mp3'){
			album_songs.push({title: item.fields.title, 'mp3': "/static/music/"+item.fields.letter+"/"+item.fields.path+"/"+item.fields.filename})
		}
	})	
	PLAYLIST = new jPlayerPlaylist({
			jPlayer: "#jquery_jplayer_1",
			cssSelectorAncestor: "#jp_container_1"
		},  album_songs, {
    		swfPath: "/static/javascript/",
			supplied: "oga, mp3",
    		solution: "flash, html"
		});	
	NOW_PLAYING = true
}

function recreate_playlist(){
	if (PLAYLIST){delete(PLAYLIST)}
	$('#jplayer_div').remove()
	$('#playlist_button_wrapper').remove()
	$('#footer').append('<div id="jplayer_div"></div>')
	$('#jplayer_div').append('<div id="jquery_jplayer_1" class="jp-jplayer"></div>')

	$('#jplayer_div').append('<div id="jp_container_1" class="jp-audio"></div>')
	$('#jp_container_1').append('<div class="jp-type-playlist"></div>')
	$('.jp-type-playlist').append('<div class="jp-gui jp-interface"></div>')
	$('.jp-interface').append('<ul class="jp-controls"></ul>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-previous" tabindex="1">previous</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-play" tabindex="1">play</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-pause" tabindex="1">pause</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-next" tabindex="1">next</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-stop" tabindex="1">stop</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-mute" tabindex="1" title="mute">mute</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-unmute" tabindex="1" title="unmute">unmute</a></li>')
	$('.jp-controls').append('<li><a href="javascript:;" class="jp-volume-max" tabindex="1" title="max volume">max volume</a></li>')
	$('.jp-interface').append('<div class="jp-progress"></div>')
	$('.jp-progress').append('<div class="jp-seek-bar"></div>')
	$('.jp-seek-bar').append('<div class="jp-play-bar"></div>')
	$('.jp-interface').append('<div class="jp-volume-bar"></div>')
	$('.jp-volume-bar').append('<div class="jp-volume-bar-value"></div>')
	$('.jp-interface').append('<div class="jp-time-holder"></div>')
	$('.jp-time-holder').append('<div class="jp-current-time"></div>')
	$('.jp-time-holder').append('<div class="jp-duration"></div>')
	$('.jp-interface').append('<ul class="jp-toggles">')
	$('.jp-toggles').append('<li><a href="javascript:;" class="jp-shuffle" tabindex="1" title="shuffle">shuffle</a></li>')
	$('.jp-toggles').append('<li><a href="javascript:;" class="jp-shuffle-off" tabindex="1" title="shuffle off">shuffle off</a></li>')
	$('.jp-toggles').append('<li><a href="javascript:;" class="jp-repeat" tabindex="1" title="repeat">repeat</a></li>')
	$('.jp-toggles').append('<li><a href="javascript:;" class="jp-repeat-off" tabindex="1" title="repeat off">repeat off</a></li>')
	$('.jp-type-playlist').append('<div class="jp-playlist"></div>')
	$('.jp-playlist').append('<ul><li></li></ul>')
	$('.jp-type-playlist').append('<div class="jp-no-solution"></div>')
	$('.jp-no-solution').append('<span>Update Required</span>')
	$('.jp-no-solution').append('To play the media you will need to either update your browser to a recent version or update your <a href="http://get.adobe.com/flashplayer/" target="_blank">Flash plugin</a>.')
	
	$('#footer').prepend('<div id="playlist_button_wrapper"></div>')
	$('#playlist_button_wrapper').append('<button id="playlist_button" onclick="show_playlist()">Show Playlist</button>')
	$('#playlist_button_wrapper').append('<button id="playlist_button" onclick="hide_playlist()">Hide Playlist</button>')
}

function show_playlist(){
	final_height =  $('.jp-playlist').height()+112
	$("#footer_wrapper").animate({height: final_height})
}

function hide_playlist(){
	$("#footer_wrapper").animate({height: '112px'})
}