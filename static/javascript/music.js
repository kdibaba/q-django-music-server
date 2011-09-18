// GLOBAL CONSTANTS

CURRENT_ALBUM = ''
PLAYLIST = ''
NOW_PLAYING = false

function add_music() {
	var answer = confirm( "Are you sure you want to Add Music?")
	if (answer){
		var type = prompt("What kind of add?")
		jQuery.ajax({
			url: "/add_music/"+type+"/", 
			success: function() {get_all_albums()},
			async	: false
		});
	}
return false;  
}

function get_song(song_id) {
	jQuery.ajax({
		url: "/song/"+song_id+"/", 
		success: function(jsonSong) {play_song(jsonSong)},
		async	: false
	});
	return "/song/"+song_id+"/" ;
};

function get_all_artists(letter) {
	jQuery.ajax({
		url: "/artists/"+letter+"/", 
		success: function(jsonArtists) {show_artists(jsonArtists)},
		async	: false
	});
};

function show_artists(jsonArtists) {
	var artists = jQuery.parseJSON(jsonArtists);
	var artist_count = 0

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="artists"></div>');
	$.each(artists, function(i,items){
		$('#artists').append('<div class="artist_albums artist_albums_'+items.pk+'"></div>');
		$('.artist_albums_'+items.pk).prepend('<div class="album_art_wrapper album_art_wrapper_' + items.pk+ '"></div>');
		artist_count+=1;		
		$.each(items.albums, function(g,item){
			$('.album_art_wrapper_'+items.pk).append('<div class="artist_album album_' + item.pk+ '"></div>');
			$('.album_' + item.pk).hover(function(){$(this).css('width',  '125px')}, function(){$(this).css('width',  '44px')});
			if (item.album_art){
				$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="get_album_show('+item.pk+')"' + '><img src="/static/music/'+ item.letter +'/' + item.folder + '/Folder.jpg' + '" /></div>' )}
			else {
				;$('.album_'+item.pk).prepend( '<div id="img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
		})
		$('.artist_albums_'+items.pk).prepend('<p onclick="get_albums_by_artist('+items.pk+')" class="artist_name" >' + items.name + '</p>');
		
	})
	$('#artists').append('</ul>');
	$('#artists').prepend('<p class="nav_header">' + artist_count + ' Artists</p>');
}

function get_all_albums(letter) {
	jQuery.ajax({
		url: "/albums/"+letter+"/", 
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
		$('#albums').append('<div class="album album_' + item.pk+ '"><h1 class="album_name">' + item.album + '</h1>' + '</div>');
		$('.album_' + item.pk).append('<h2 onclick="get_albums_by_artist('+item.artist_id+')">' + item.artist + '</h2>')
		$('.album_' + item.pk).append('<h3>' + item.year + ' | ' + item.song_count + ' SONGS</h3>')
		if (item.album_art){
			//cover_count += 1;
			$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="get_album_show('+item.pk+')"' + '><img src="/static/music/'+ item.letter +'/' + item.folder + '/Folder.jpg' + '" /></div>' )}
		else {
			//missing_cover_count += 1
			;$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="get_album_show('+item.pk+')"' + '><img src="/static/images/default_album_art.jpg" /></div>' )
		}
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
		async	: false
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
	var all_album = jQuery.parseJSON(jsonAlbum);

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="album"></div>');
	//get_album_info(all_album.pk);
	
	$('#album').append('<h1>'+ all_album[0].album +'</h1><div class="current_album"></div>')
	
	$.each(all_album, function(i,album){
		if (album.album_art){$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/music/' +album.letter+ '/' + album.folder + '/Folder.jpg' + '" /></div>' )}
		else {$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
		$('.current_album').append( '<button id="play_album_button" onclick="get_album_play('+album.pk+')">PLAY ALBUM</button>')
		$('.current_album').append( '<h2 onclick="get_albums_by_artist('+album.artist_id+')">'+ album.artist+'</h2>')
		$('.current_album').append( '<h3>'+ album.year+' | '+album.song_count+' SONGS</h3>')
		
		CURRENT_ALBUM = ''
		$('#album').append('<table id="song_table"><tr><th></th><th>Title</th><th>Length</th><th>Rating</th></tr></table>')
		$.each(album.songs, function(i,item){
			if (item.type == "mp3"){
				$('#song_table').append("<tr class='songs' id='song_" + item.pk + "'><td class='play_song_button' onclick=\"get_song(" + item.pk + ")\"></td><td ondblclick=\"get_song(" + item.pk + ")\">" + item.title + "</td><td>" + item.length + "</td><td id='rating_td'>" + get_rating_html(item.rating, item.pk) + "</td>");
				
			}
		})
	
	})	
	if (show_or_play == 2){play_album(jsonAlbum)}
}

function get_rating_html(rating, song_id){
	var html = ''
	var i = 0
	for (i=1; i<=5; i++){
		if (i <= rating){
			html += '<div class="ratings rated rating_' + i + '_'+ song_id + '" onclick="set_rating('+ i + ', ' + song_id + ')"></div>'
		}
		else {
			html += '<div class="ratings unrated rating_' + i + '_' + song_id + '" onclick="set_rating('+ i + ', ' + song_id + ')"></div>'
		}
	}
	return html
}

function set_rating(rating, song_id){
	jQuery.ajax({
		url: "/rating/" + song_id + "/" + rating + "/",
		success: function(success){	update_rating(rating, song_id)},
		async:   false
	});
}
	
function update_rating(rating, song_id){
	var i = 0
	for (i=1; i<=5; i++){
		if (i <= rating) {
			$('.rating_'+ i +'_'+song_id).removeClass('unrated').addClass('rated')
		}
		else {
			$('.rating_'+ i +'_'+song_id).removeClass('rated').addClass('unrated')			
		}
	}
}


function play_song(jsonSong) {
	song = jQuery.parseJSON(jsonSong);
	$('.songs').removeClass("now_playing")
	$('#song_' + song.pk).addClass("now_playing")
	
	//If playlist is being displayed when some	one wants to play a single song,
	//Hide the playlist.
	if (PLAYLIST){hide_playlist()}
	var destiny = song.full_path;
	
	recreate_playlist();
	PLAYLIST = new jPlayerPlaylist({
		jPlayer: "#jquery_jplayer_1",
		cssSelectorAncestor: "#jp_container_1"
	},  [{	title: song.title,
			'mp3': destiny}],
		{
		swfPath: "/static/javascript/",
		supplied: "mp3",
		solution: "flash, html"
	});	
	NOW_PLAYING = true
}

function play_album(jsonAlbum){
	$('.songs').removeClass("now_playing")
	var album = jQuery.parseJSON(jsonAlbum);
	recreate_playlist();
	var album_songs = []
	$.each(album[0].songs, function(i,item){
		if (item.type == 'mp3'){
			album_songs.push({title: item.title, 'mp3': "/static/music/"+item.letter+"/"+item.path+"/"+item.filename})
		}
	})	
	PLAYLIST = new jPlayerPlaylist({
			jPlayer: "#jquery_jplayer_1",
			cssSelectorAncestor: "#jp_container_1"
		},  album_songs, {
    		swfPath: "/static/javascript/",
			supplied: "mp3",
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