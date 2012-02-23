// GLOBAL CONSTANTS

CURRENT_ALBUM = ''
PLAYLIST = ''
NOW_PLAYING = false

function handle_hash(){
	var destination = location.hash.replace('#', '')
	destination = destination.split('/')
	if (check_session_status()){
		if (destination[1] == 'artists') {
			if (parseInt(destination[3]) == 0){
				display_message('Retrieving Artists....');
				get_all_artists(destination[2], parseInt(destination[3]));
			}
			else if (!ARTISTS_CONTENT){
				display_message('Retrieving Artists....');
				get_all_artists(destination[2], parseInt(destination[3]));			
			}
			else if (ARTISTS_PAGE != destination[3]){
				display_message('Retrieving Artists....');
				get_all_artists(destination[2], parseInt(destination[3]));			
			}
		}
		else if (destination[1] == 'albums') {
			if (parseInt(destination[3]) == 0){
				display_message('Retrieving Albums....');
				get_all_albums(destination[2], parseInt(destination[3]));
			}
			else if (!ALBUMS_CONTENT){
				display_message('Retrieving Albums....');
				get_all_albums(destination[2], parseInt(destination[3]));			
			}
			else if (ALBUMS_PAGE != destination[3]){
				display_message('Retrieving Albums....');
				get_all_albums(destination[2], parseInt(destination[3]));			
			}
		}
		else if (destination[1] == 'albums_by_artist') {
			display_message('Retrieving Albums by '+destination[2] +'....');
			get_albums_by_artist(destination[2]);
		}
		else if (destination[1] == 'albums_by_genre') {
			display_message('Retrieving Albums by genre '+destination[2] +'....');
			get_albums_by_genre(destination[2]);
		}		
		else if (destination[1] == 'album_show') {
			get_album_show(destination[2]);
		}
		else if (destination[1] == 'album_delete') {
			delete_album(destination[2]);
		}
		else if (destination[1] == 'albums_by_year') {
			if (parseInt(destination[3]) == 0){
				display_message('Retrieving Albums from '+destination[2] +'....');
				get_albums_by_year(destination[2], parseInt(destination[3]));
			}
			else if (!ALBUMS_CONTENT){
				display_message('Retrieving Albums from '+destination[2] +'....');
				get_albums_by_year(destination[2], parseInt(destination[3]));			
			}
			else if (ALBUMS_PAGE != destination[3]){
				display_message('Retrieving Albums from '+destination[2] +'....');
				get_albums_by_year(destination[2], parseInt(destination[3]));
			}
		}
		else if (destination[1] == 'rebuild') {
			display_message('Rebuilding Database....');
			rebuild(destination[2]);
		}
		else if (destination[1] == 'search') {
			display_message('Searching Database....');
			search_artists(destination[2]);
		}
	}
	else {
		window.location=window.location.host
	}
}

function display_message(message) {
	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="message"></div>');
	var opts = {
			  lines: 14, // The number of lines to draw
			  length: 23, // The length of each line
			  width: 8, // The line thickness
			  radius: 26, // The radius of the inner circle
			  color: '#000', // #rgb or #rrggbb
			  speed: 1, // Rounds per second
			  trail: 60, // Afterglow percentage
			  shadow: false // Whether to render a shadow
			};
	var target = document.getElementById('message');	
	var spinner = new Spinner(opts).spin(target);
	
	$('#message').append('<div style="margin-top: 75px;">' + message + '</div>');
}

function display_message_alert(message, status) {
	var status_message = $('#status_message')
	status_message = status_message.html(message);
	
	if (status) { status_message.addClass('good'); }
	else { status_message.addClass('bad'); }
	
	status_message.slideDown();
	setTimeout("$('#status_message').slideUp(500, function(){$('#status_message').removeClass('good');$('#status_message').removeClass('bad');})", 4000)
	
}
function add_music(type) {
	jQuery.ajax({
		url: "/add_music/"+type+"/", 
		success: function() {get_all_albums('all', 0)},
		async	: false
	});
	return false;  
}

function check_session_status(){
	var logged_in = true
	jQuery.ajax({
		url: "/check_session/", 
		success: function(status) {if (status == 0){logged_in = false}},
		async	: false
	});
	return logged_in;  
}

function search_artists(text) {
	
	jQuery.ajax({
		url: "/search_music_artists/?query="+text, 
		success: function(jsonArtists) {show_results_artists(jsonArtists, text); search_albums(text);},
		async	: true
	});
}
function search_albums(text) {
	jQuery.ajax({
		url: "/search_music_albums/?query="+text, 
		success: function(jsonAlbums) {show_results_albums(jsonAlbums, text); search_songs(text)},
		async	: true
	}); 
}

function search_songs(text) {
	jQuery.ajax({
		url: "/search_music_songs/?query="+text, 
		success: function(jsonSongs) {show_results_songs(jsonSongs, text)},
		async	: true
	});
}

function show_results(field) {
	$('#nav_header_albums').removeClass('selected');
	$('#nav_header_artists').removeClass('selected');
	$('#nav_header_songs').removeClass('selected');
	$('#albums').hide();
	$('#artists').hide();
	$('#songs').hide();
	$('#nav_header_'+field).addClass('selected');
	$('#'+field).show();
}


function show_results_artists(jsonArtists, letter) {
	var artists = jQuery.parseJSON(jsonArtists);
	var artist_count = 0
	var deg = 0
	var length = 0
	
	$('#content').replaceWith('<div id="content" style="display:none"></div>')
	$('#content').append('<div id="artists"></div>');
	$.each(artists, function(i,items){
		$('#artists').append('<div class="artist_albums artist_albums_'+items.pk+'"></div>');
		$('.artist_albums_'+items.pk).prepend('<div class="album_art_wrapper album_art_wrapper_' + items.pk+ '"></div>');
		artist_count+=1;
		deg = 15
		length = items.albums.length - 1;
		$.each(items.albums, function(g,item){
			if (length == g){ deg = 0;}
			$('.album_art_wrapper_'+items.pk).append('<div class="artist_album album_' + item.pk+ '" style="-webkit-transform: rotate('+ deg + 'deg); -moz-transform: rotate('+ deg + 'deg)"></div>');
			if (item.album_art){
				$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/albums_by_artist/'+items.pk+'\'"><img src="/static/music/'+ item.letter +'/' + item.folder + '/Folder.jpg' + '" /></div>' )}
			else {
				$('.album_'+item.pk).prepend( '<div id="img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
			deg += 15;
		})
		$('.artist_albums_'+items.pk).append('<div class="artist_info artist_info_' + items.pk + '"><h1 onclick="location.href=\'/#/albums_by_artist/'+items.pk+'\'">' + items.name + '</h1></div>');
		$('.artist_info_' + items.pk).append('<h2>'+items.album_count+' Albums<h2>');
		$('.artist_info_' + items.pk).append('<h2>'+items.song_count+' Songs<h2>');
		
	})
	$('#artists').append('</ul>');
	$('#content').prepend('<div id="nav_headers"></div>')
	$('#nav_headers').prepend('<a id="nav_header_artists"  class="selected" onclick="show_results(\'artists\')">Artist (' + artist_count + ')</a>');
	$('#content').show();
	$('#nav_headers').append('<a id="nav_header_albums" onclick="show_results(\'albums\')">Albums </a>');
	$('#nav_headers').append('<a id="nav_header_songs" onclick="show_results(\'songs\')">Songs </a>');
	var opts = {
			  lines: 10, // The number of lines to draw
			  length: 4, // The length of each line
			  width: 4, // The line thickness
			  radius: 5, // The radius of the inner circle
			  color: '#000', // #rgb or #rrggbb
			  speed: 2.2, // Rounds per second
			  trail: 41, // Afterglow percentage
			  shadow: true, // Whether to render a shadow
			  hwaccel: false // Whether to use hardware acceleration
			};
	var target1 = document.getElementById('nav_header_albums');	
	var spinner1 = new Spinner(opts).spin(target1);
	$('#nav_header_albums > div').css({"left": "74px", "display" : "inline-block", "top":"-6px"});
	
	var target2 = document.getElementById('nav_header_songs');	
	var spinner2 = new Spinner(opts).spin(target2);
	$('#nav_header_songs > div').css({"left": "74px", "display" : "inline-block", "top":"-6px"});

	$('#artists').css('width', ARTISTS_HOR*265+'px')
}

function show_results_albums(jsonAlbums) {
	var albums = jQuery.parseJSON(jsonAlbums);
	var album_count = 0
	
	$('#content').append('<div id="albums" style="display:none"></div>');
	$.each(albums, function(i,item){
		album_count+=1;
		$('#albums').append('<div class="album album2_' + item.pk+ '"><h1 class="album_name">' + item.album + '</h1>' + '</div>');
		$('.album2_' + item.pk).append('<h2 onclick="location.href=\'/#/albums_by_artist/'+item.artist_id+'\'">' + item.artist + '</h2>')
		$('.album2_' + item.pk).append('<h3> <item class="year" onclick="location.href=\'/#/albums_by_year/'+item.year+'\'">' + item.year + '</item> | ' + item.song_count + ' SONGS | ' + item.album_size + '</h3>')
		if (item.album_art){
			$('.album2_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/album_show/'+item.pk+'\'"' + '><img src="/static/music/'+ item.letter +'/' + item.folder + '/Folder.jpg' + '" /></div>' )}
		else {
			$('.album2_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/album_show/'+item.pk+'\'"' + '><img src="/static/images/default_album_art.jpg" /></div>' )
		}
	})
	$('#nav_header_albums').replaceWith('<a id="nav_header_albums" onclick="show_results(\'albums\')">Album (' + album_count + ')</a>')
	$('#albums').css('width', ALBUMS_HOR*200+'px')
}

function show_results_songs(jsonSongs) {
	var all_album = jQuery.parseJSON(jsonSongs);
	var song_count = 0;
	
	$('#content').append('<div id="songs"></div>');
	
	//$('#album').append( '<button id="delete_album_button" style="float:right;" onclick="delete_album('+all_album[0].pk+')">DELETE ALBUM</button>')
	$('#songs').append('<div id="current_album_songs"></div>')
	
	$('#current_album_songs').append('<div id="song_table_wrapper"><table id="song_table" class="rounder-top"></table></div>')
	$('#song_table').append('<tr id="song_table_header" class="rounder-top"></tr>')
	$('#song_table_header').append('<th class="title_column">Title</th><th class="artist_column">Artist</th><th class="genre_column">Genre</th><th class="play_column">Play</th><th class="add_column">Add</th><th class="length_column">Length</th><th class="file_size_column">File Size</th><th class="rating_column">Rating</th>')
		
	$.each(all_album, function(i,item){
		song_count+=1;
		if (item.type == "mp3"){
			$('#song_table').append("<tr class='songs' id='song_" + item.pk + "'><td class=\"title_column song_table_field\" ondblclick=\"get_song(" + item.pk + 
					", 'play')\">" + item.title + "</td><td class='artist_column song_table_field'>" + item.artist + "</td><td class='genre_column song_table_field'>" + item.genre + "</td><td  class=\"play_column song_table_field play_song_button\" title='Click here to play song.' onclick=\"get_song(" + 
					item.pk + ", 'play')\"></td><td  class=\"add_column song_table_field add_song_button\" title='Click here to add to playlist.' onclick=\"get_song(" + item.pk + 
					", 'add')\"></td><td class='length_column song_table_field'>" + item.length +  "</td><td class='file_size_column song_table_field'>" + item.file_size + "</td><td id='rating_td' class='rating_column song_table_field'>" + get_rating_html(item.rating, item.pk) + 
					"</td></tr>");
			
		}
	})
	$('#nav_header_songs').replaceWith('<a id="nav_header_songs" onclick="show_results(\'songs\')">Songs (' + song_count + ')')
	//$('#nav_headers').append();
	

	var table_height = $("#song_table_wrapper").height()
	var content_height = $(window).height()-300
	if (content_height < table_height) { $('#song_table_wrapper').css('height', content_height+'px');}
	$('#songs').prepend('<div id="song_column_selectors"></div>')
	$('#songs').prepend('<div id="album_settings"><img src="/static/images/settings_small.png"></div>')
	$('#song_column_selectors').append('<div class="select_artist selected"><div class="checked"></div>Artist</div>')
	$('#song_column_selectors').append('<div class="select_genre selected"><div class="checked"></div>Genre</div>')
	$('#song_column_selectors').append('<div class="select_length selected"><div class="checked"></div>Length</div>')
	$('#song_column_selectors').append('<div class="select_file_size selected"><div class="checked"></div>File Size</div>')
	$('#song_column_selectors').append('<div class="select_rating selected"><div class="checked"></div>Rating</div>')
	song_column_selector_handler();
	$('#songs').hide()
}

function rebuild(letter) {
	jQuery.ajax({
		url: "/rebuild/"+letter+"/", 
		success: function() {get_all_artists(letter)},
		async	: false
	});
	return false;  
}

function get_song(song_id, play_or_add) {
	jQuery.ajax({
		url: "/song/"+song_id+"/", 
		success: function(jsonSong){
			if(play_or_add == 'play'){
				play_song(jsonSong);
				}
			else if(play_or_add == 'add') {
				add_song(jsonSong);
				}
			},
		async	: false
	});
	return "/song/"+song_id+"/" ;
};

function get_all_artists(letter, page) {
	jQuery.ajax({
		url: "/artists/"+letter+"/", 
		success: function(jsonArtists) {show_artists(jsonArtists, letter, page)},
		async	: true
	});
};

function show_artists(jsonArtists, letter, page) {
	var artists = jQuery.parseJSON(jsonArtists);
	ARTISTS_CONTENT = artists;
	ARTISTS_PREV = ''
	ARTISTS_CURR = ''
	ARTISTS_NEXT = ''
	ARTISTS_PAGE = page
	ARTISTS_LETTER = letter

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="artists"></div>');
	
	build_artist_page()
		
}

function next_artist_page() {
	ARTISTS_PAGE += 1

	//ARTISTS_PREV = ARTISTS_CURR
	$('#artists').animate({opacity : 0, "margin-left" : "-1000px"}, 500, function(){
		$('#artists').html('')
		build_artist_page();
		$('#artists').css({"margin" : "auto", opacity : 1}).show(200);
	})
	location.hash = '/artists/'+ARTISTS_LETTER+'/'+ARTISTS_PAGE+'/'
}

function previous_artist_page() {
	ARTISTS_PAGE -= 1

	//ARTISTS_NEXT = ARTISTS_CURR
	$('#artists').animate({opacity : 0, "margin-left" : "1000px"}, 500, function(){
		$('#artists').html('')
		build_artist_page();
		$('#artists').css({"margin" : "auto", opacity : 1}).show(200);
	})
	location.hash = '/artists/'+ARTISTS_LETTER+'/'+ARTISTS_PAGE+'/'
}

function build_artist_page() {

	var artist_count = 0
	var deg = 0
	var length = 0
	var cover_count = 0;
	var missing_cover_count = 0;
	
	var iterator = ARTISTS_PAGE * ARTISTS_COUNT
	
	if (ARTISTS_PAGE == 0){$('#prev_page').remove()}
	else if(!$('#prev_page').html()){$('#content').append('<button id="prev_page" onclick="previous_artist_page();" style="width: 31px; left: 0px; padding-bottom: 0px; "><img src="/static/images/prev.png" /></button>')}
	
	if (ARTISTS_CONTENT.length - iterator <= ARTISTS_COUNT){$('#next_page').remove()}
	else if(!$('#next_page').html()){$('#content').append('<button id="next_page" onclick="next_artist_page();" style="width: 31px; right: 0px; padding-bottom: 0px; "><img src="/static/images/next.png" /></button>')}
	
	$.each(ARTISTS_CONTENT, function(i,items){
		if (i >= iterator && i < iterator + ARTISTS_COUNT ) {
			$('#artists').append('<div class="artist_albums artist_albums_'+items.pk+'"></div>');
			$('.artist_albums_'+items.pk).prepend('<div class="album_art_wrapper album_art_wrapper_' + items.pk+ '"></div>');
			artist_count+=1;
			deg = 15
			length = items.albums.length - 1;
			$.each(items.albums, function(g,item){
				if (length == g){ deg = 0;}
				$('.album_art_wrapper_'+items.pk).append('<div class="artist_album album_' + item.pk+ '" style="-webkit-transform: rotate('+ deg + 'deg); -moz-transform: rotate('+ deg + 'deg)"></div>');
				//$('.album_' + item.pk).hover(function(){$(this).css('width',  '125px')}, function(){$(this).css('width',  '44px')});
				if (item.album_art){
					//cover_count += 1;
					$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/albums_by_artist/'+items.pk+'\'"><img src="/static/music/'+ item.letter +'/' + item.folder + '/Folder.jpg' + '" /></div>' )}
				else {
					//missing_cover_count += 1
					$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/albums_by_artist/'+items.pk+'\'"><img src="/static/images/default_album_art.jpg" /></div>' )}
				deg += 15;
			})
			$('.artist_albums_'+items.pk).append('<div class="artist_info artist_info_' + items.pk + '"><h1 onclick="location.href=\'/#/albums_by_artist/'+items.pk+'\'">' + items.name + '</h1></div>');
			$('.artist_info_' + items.pk).append('<h2>'+items.album_count+' Albums<h2>');
			$('.artist_info_' + items.pk).append('<h2>'+items.song_count+' Songs<h2>');
		}
	})
	$('#artists').append('</ul>');
	if (user_is_admin()) {
		//$('#artists').prepend('<p class="nav_header">' + ARTISTS_CONTENT.length + ' Artist(s) found. <button id="rebuild_button" onclick="location.href=\'/#/rebuild/'+ARTISTS_LETTER+'\'">Rebuild '+ARTISTS_LETTER+'</button> </p>');
		$('#artists').prepend('<p class="nav_header">' + ARTISTS_CONTENT.length + ' Artist(s) found.')
	}
	else {
		$('#artists').prepend('<p class="nav_header">' + ARTISTS_CONTENT.length + ' Artist(s) found.')
	}
	//alert('Cover Count = ' + cover_count);
	//alert('Missing Cover Count = ' + missing_cover_count);
	ARTISTS_CURR = $('#artists');
	$('#artists').css('width', ARTISTS_HOR*265+'px')
}

function user_is_admin() {
	var admin = false
	jQuery.ajax({
		url: "/is_admin/", 
		success: function(status) { if (status == 1){ admin = true}},
		async	: false
	});	
	return admin
}

function get_all_albums(letter, page) {
	jQuery.ajax({
		url: "/albums/"+letter+"/", 
		success: function(jsonAlbums) {show_albums(jsonAlbums, letter, '' , page)},
		async	: true
	});
};

function show_albums(jsonAlbums, letter, year, page) {
	var albums = jQuery.parseJSON(jsonAlbums);
	ALBUMS_CONTENT = albums;
	ALBUMS_PREV = ''
	ALBUMS_CURR = ''
	ALBUMS_NEXT = ''
	ALBUMS_PAGE = page
	if(letter){
		ALBUMS_LETTER = letter
		ALBUMS_YEAR = ''
	}
	else if (year){
		ALBUMS_YEAR = year
		ALBUMS_LETTER = ''
	}

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="albums"></div>');
	
	build_album_page()
		
}


function next_album_page() {
	ALBUMS_PAGE += 1

	//ARTISTS_PREV = ARTISTS_CURR
	$('#albums').animate({opacity : 0, "margin-left" : "-1000px"}, 500, function(){
		$('#albums').html('')
		build_album_page();
		$('#albums').css({"margin" : "auto", opacity : 1}).show(200);
	})
	if(ALBUMS_LETTER){
		location.hash = '/albums/'+ALBUMS_LETTER+'/'+ALBUMS_PAGE+'/';
	}
	else if(ALBUMS_YEAR){
		location.hash = '/albums_by_year/'+ALBUMS_YEAR+'/'+ALBUMS_PAGE+'/';
	}
}

function previous_album_page() {
	ALBUMS_PAGE -= 1

	//ARTISTS_NEXT = ARTISTS_CURR
	$('#albums').animate({opacity : 0, "margin-left" : "1000px"}, 500, function(){
		$('#albums').html('')
		build_album_page();
		$('#albums').css({opacity : 1, "margin" : "auto"}).show(200);
	})
	if(ALBUMS_LETTER){
		location.hash = '/albums/'+ALBUMS_LETTER+'/'+ALBUMS_PAGE+'/';
	}
	else if(ALBUMS_YEAR){
		location.hash = '/albums_by_year/'+ALBUMS_YEAR+'/'+ALBUMS_PAGE+'/';
	}
}


function build_album_page() {

	var cover_count = 0;
	var missing_cover_count = 0;
	
	var iterator = ALBUMS_PAGE * ALBUMS_COUNT

	if (ALBUMS_PAGE == 0){$('#prev_page').remove()}
	else if(!$('#prev_page').html()){$('#content').append('<button id="prev_page" onclick="previous_album_page();" style="width: 31px; left: 0px; padding-bottom: 0px; "><img src="/static/images/prev.png" /></button>')}
	
	if (ALBUMS_CONTENT.length - iterator <= ALBUMS_COUNT){$('#next_page').remove()}
	else if(!$('#next_page').html()){$('#content').append('<button id="next_page" onclick="next_album_page();" style="width: 31px; right: 0px; padding-bottom: 0px; "><img src="/static/images/next.png" /></button>')}
	
	$.each(ALBUMS_CONTENT, function(i,item){

		if (i >= iterator && i < iterator + ALBUMS_COUNT ) {
			$('#albums').append('<div class="album album_' + item.pk+ '"><h1 class="album_name">' + item.album + '</h1>' + '</div>');
			$('.album_' + item.pk).append('<h2 onclick="location.href=\'/#/albums_by_artist/'+item.artist_id+'\'">' + item.artist + '</h2>')
			$('.album_' + item.pk).append('<h3> <item class="year" onclick="location.href=\'/#/albums_by_year/'+item.year+'/0/\'">' + item.year + '</item> | ' + item.song_count + 
					' SONGS | ' + item.album_size + ' | <item class="genre" onclick="location.href=\'/#/albums_by_genre/'+item.genre_id+'/0/\'">' + item.genre + '</h3>')
			if (item.album_art){
				//cover_count += 1;
				$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/album_show/'+item.pk+'\'"' + '><img src="/static/music/'+ item.letter +'/' + item.folder + '/Folder.jpg' + '" /></div>' )}
			else {
				//missing_cover_count += 1
				$('.album_'+item.pk).prepend( '<div id="img_div"' + ' onclick="location.href=\'/#/album_show/'+item.pk+'\'"' + '><img src="/static/images/default_album_art.jpg" /></div>' )
			}
		}
	})
	$('#albums').prepend('<p class="nav_header">' + ALBUMS_CONTENT.length + ' Albums</p>');
	//alert('Cover Count = ' + cover_count);
	//alert('Missing Cover Count = ' + missing_cover_count);
	$('#albums').css('width', ALBUMS_HOR*180+'px')
}

function get_albums_by_artist(artist_id) {
	$.get("/albums_by_artist/" + artist_id + "/", function(jsonAlbums) {
	        show_albums(jsonAlbums, '', '', 0);
	});
};


function get_albums_by_genre(genre_id) {
	$.get("/albums_by_genre/" + genre_id + "/", function(jsonAlbums) {
	        show_albums(jsonAlbums, '', '', 0);
	});
};


function get_albums_by_year(year_id) {
	$.get("/albums_by_year/" + year_id + "/", function(jsonAlbums) {
	        show_albums(jsonAlbums, '', year_id, 0);
	});
};

function get_album_show(album_id) {
	jQuery.ajax({
		url: "/album_show/" + album_id + "/", 
		success: function(jsonAlbum) {show_album(jsonAlbum, 1);},
		async	: false
	});
};

function delete_album(album_id) {
	jQuery.ajax({
		url: "/album_delete/" + album_id + "/", 
		success: function(message) {get_albums_by_artist(message);},
		async	: false
	});
};

function get_album_play(album_id) {
	jQuery.ajax({
		url: "/album_show/" + album_id + "/", 
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
	
	$('#album').append('<div class="current_album"></div>')
	//$('#album').append( '<button id="delete_album_button" style="float:right;" onclick="delete_album('+all_album[0].pk+')">DELETE ALBUM</button>')
	$('#album').append('<div id="current_album_songs"></div>')
	$.each(all_album, function(i,album){
		if (album.album_art){$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/music/' +album.letter+ '/' + album.folder + '/Folder.jpg' + '" /></div>' )}
		else {$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
		$('.current_album').append( '<button id="play_album_button" onclick="get_album_play('+album.pk+')">PLAY ALBUM</button>')
		$('.current_album').append( '<h2 onclick="location.href=\'/#/albums_by_artist/'+album.artist_id+'\'">'+ album.artist+'</h2>')
		$('.current_album').append( '<h3> <item class="year" onclick="location.href=\'/#/albums_by_year/'+album.year+'\'">' + album.year + '</item> | '+album.song_count+' SONGS | ' + album.album_size + '</h3>')
		
		CURRENT_ALBUM = ''
		$('#current_album_songs').append('<h1>'+ all_album[0].album +'</h1>')
		$('#current_album_songs').append('<div id="song_table_wrapper"><table id="song_table" class="rounder-top"></table></div>')
		$('#song_table').append('<tr id="song_table_header" class="rounder-top"></tr>')
		$('#song_table_header').append('<th class="title_column">Title</th><th class="artist_column">Artist</th><th class="genre_column">Genre</th><th class="play_column">Play</th><th class="add_column">Add</th><th class="length_column">Length</th><th class="file_size_column">File Size</th><th class="rating_column">Rating</th>')
		$.each(album.songs, function(i,item){
			if (item.type == "mp3"){
				$('#song_table').append("<tr class='songs' id='song_" + item.pk + "'><td class=\"title_column song_table_field\" ondblclick=\"get_song(" + item.pk + 
						", 'play')\">" + item.title + "</td><td class='artist_column song_table_field'>" + item.artist + "</td><td class='genre_column song_table_field'>" + item.genre + "</td><td  class=\"play_column song_table_field play_song_button\" title='Click here to play song.' onclick=\"get_song(" + 
						item.pk + ", 'play')\"></td><td  class=\"add_column song_table_field add_song_button\" title='Click here to add to playlist.' onclick=\"get_song(" + item.pk + 
						", 'add')\"></td><td class='length_column song_table_field'>" + item.length +  "</td><td class='file_size_column song_table_field'>" + item.file_size + "</td><td id='rating_td' class='rating_column song_table_field'>" + get_rating_html(item.rating, item.pk) + 
						"</td></tr>");
				
			}
		})
	
	})
	if (show_or_play == 2){play_album(jsonAlbum)}
	else {
		var table_height = $("#song_table").height()
		var content_height = $(window).height()-310
		if (content_height < table_height) { $('#song_table_wrapper').css('height', content_height+'px');}
		//else {$('#song_table').css('height', content_height+'px');}
		$('#album').prepend('<div id="song_column_selectors"></div>')
		$('#album').prepend('<div id="album_settings"><img src="/static/images/settings_small.png"></div>')
		$('#song_column_selectors').append('<div class="select_artist selected"><div class="checked"></div>Artist</div>')
		$('#song_column_selectors').append('<div class="select_genre selected"><div class="checked"></div>Genre</div>')
		$('#song_column_selectors').append('<div class="select_length selected"><div class="checked"></div>Length</div>')
		$('#song_column_selectors').append('<div class="select_file_size selected"><div class="checked"></div>File Size</div>')
		$('#song_column_selectors').append('<div class="select_rating selected"><div class="checked"></div>Rating</div>')
		song_column_selector_handler();
	}
}

function song_column_selector_handler() {
	
	$('#album_settings').click(function() {$('#song_column_selectors').toggle()})
	$('.select_artist').click(function() {
		$('.artist_column').toggle();
		$('.select_artist').toggleClass("selected");
		set_profile_song_columns('artist');
		})		
	$('.select_genre').click(function() {
		$('.genre_column').toggle();
		$('.select_genre').toggleClass('selected');
		set_profile_song_columns('genre');
		})
	$('.select_length').click(function() {
		$('.length_column').toggle();
		$('.select_length').toggleClass('selected');
		set_profile_song_columns('length');})
	$('.select_file_size').click(function() {
		$('.file_size_column').toggle();
		$('.select_file_size').toggleClass('selected');
		set_profile_song_columns('file_size');})
	$('.select_rating').click(function() {
		$('.rating_column').toggle();
		$('.select_rating').toggleClass('selected');
		set_profile_song_columns('rating');})
		
	get_profile_song_columns();
}

function get_profile_song_columns() {
	jQuery.ajax({
		url: "/get_profile_song_columns/",
		success: function(columns){
			columns = jQuery.parseJSON(columns).split(';')
			for (i = 0; i < columns.length; i++){
				$('.'+columns[i]+'_column').toggle();
				$('.select_'+columns[i]).toggleClass("selected");
				}
		},
		async:   false
	});
}

function set_profile_song_columns(field){
	jQuery.ajax({
		url: "/set_profile_song_columns/?query="+field,
		failure: function(){
			display_message_alert('Failed.', false);
		},
		async:   false
	});
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
		success: function(message){	
					if (message == 0){display_message_alert('You do not have sufficient previleges to rate music.', false)}
					else if (message == 1) {display_message_alert('Rating successfully applied.', true); update_rating(rating, song_id)}
					else {display_message_alert('Rating was not applied.', false); }},
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
	//$('.songs').removeClass("now_playing")
	//$('#song_' + song.pk).addClass("now_playing")
	
	//If playlist is being displayed when some	one wants to play a single song,
	//Hide the playlist.
	if (PLAYLIST){hide_playlist()}
	var destiny = song.full_path;
	
	recreate_playlist();
	PLAYLIST = new jPlayerPlaylist({
		jPlayer: "#jquery_jplayer_1",
		cssSelectorAncestor: "#jp_container_1"
	},  [{	title: song.title,
			artist: song.artist,
			'mp3': destiny}],
		{
		swfPath: "/static/javascript/",
		supplied: "mp3",
		solution: "flash, html"
	});	
	NOW_PLAYING = true
}


function add_song(jsonSong) {
	song = jQuery.parseJSON(jsonSong);
	//$('.songs').removeClass("now_playing")
	//$('#song_' + song.pk).addClass("now_playing")
	
	var destiny = song.full_path;
	if(!jQuery.isEmptyObject(PLAYLIST.playlist)){
		PLAYLIST.add({
			title: song.title,
			artist: song.artist,
			'mp3': destiny});
	}
	else {
		recreate_playlist();
		PLAYLIST = new jPlayerPlaylist({
			jPlayer: "#jquery_jplayer_1",
			cssSelectorAncestor: "#jp_container_1"
		},  [{	title: song.title,
				artist: song.artist,
				'mp3': destiny}],
			{
			swfPath: "/static/javascript/",
			supplied: "mp3",
			solution: "flash, html"
		});	
		NOW_PLAYING = true
	}		
	show_playlist()
}

function play_album(jsonAlbum){
	$('.songs').removeClass("now_playing")
	var album = jQuery.parseJSON(jsonAlbum);
	recreate_playlist();
	var album_songs = []
	$.each(album[0].songs, function(i,item){
		if (item.type == 'mp3'){
			album_songs.push({title: item.title, artist: item.artist, 'mp3': "/static/music/"+item.letter+"/"+item.path+"/"+item.filename})
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
	$('#playlist_button_wrapper').append('<button id="close_button" onclick="destroy_playlist()">X</button>')
	$('div.jp-progress').css("width", $(window).width()-340+'px')
	$('div.jp-time-holder').css("width", $(window).width()-350+'px')
	$('.jp-toggles').css("left", $(window).width()/2+'px');
	
}

function show_playlist(){
	final_height =  $('.jp-playlist').height()+132
	$("#footer_wrapper").animate({height: final_height})
}

function hide_playlist(){
	$("#footer_wrapper").animate({height: '112px'})
}

function destroy_playlist(){
	if (PLAYLIST){delete(PLAYLIST)}
	$('#jplayer_div').remove()
	$('#playlist_button_wrapper').remove()
	PLAYLIST = ''
}