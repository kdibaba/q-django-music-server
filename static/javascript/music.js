// GLOBAL CONSTANTS

CURRENT_ALBUM = ''
	
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
		$('#artists').append('<div onclick="get_albums_by_artist('+item.pk+')">' + item.fields.artist + ' </div>');
	})
	$('#artists').append('</ul>');
	$('#artists').prepend('<p class="nav_header">' + artist_count + ' Artists</p>');
}

function get_all_albums() {
	$.get("/albums/", function(jsonAlbums) {
		show_albums(jsonAlbums);
	});
};

function show_albums(jsonAlbums) {
	var albums = jQuery.parseJSON(jsonAlbums);
	var album_count = 0

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="albums"></div>');
	$.each(albums, function(i,item){
		album_count+=1;
		$('#albums').append('<div class="album album_' + item.pk + '" onclick="get_album('+item.pk+')">' + '<h1>' + item.fields.album + '</h1>' + '</div>');
		if (item.fields.album_art){$('.album_'+item.pk).append( '<div id="img_div"><img src="/static/music/'+ item.fields.letter +'/' + item.fields.folder + '/Folder.jpg' + '" /></div>' )}
		else {$('.album_'+item.pk).append( '<div id="img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
	})
	$('#albums').prepend('<p class="nav_header">' + album_count + ' Albums</p>');
}

function get_albums_by_artist(artist_id) {
	$.get("/albums/" + artist_id + "/", function(jsonAlbums) {
	        show_albums(jsonAlbums);
	});
};

function get_album(album_id) {
	jQuery.ajax({
		url: "/album/" + album_id + "/", 
		success: function(jsonAlbum) {show_album(jsonAlbum);},
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

function show_album(jsonAlbum) {
	var album = jQuery.parseJSON(jsonAlbum);

	$('#content').replaceWith('<div id="content"></div>')
	$('#content').append('<div id="album"></div>');
	get_album_info(album[0].fields.album);
	
	$('#album').append('<div class="current_album"></div>')
	$.each(CURRENT_ALBUM, function(i,item){
		if (item.fields.album_art){$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/music/' +item.fields.letter+ '/' + item.fields.folder + '/Folder.jpg' + '" /></div>' )}
		else {$('.current_album').append( '<div id="curr_album_img_div"><img src="/static/images/default_album_art.jpg" /></div>' )}
	})
	CURRENT_ALBUM = ''
	
	$('#album').append('<table id="song_table"><tr><th>Title</th><th>Length</th></tr></table>')
	$.each(album, function(i,item){
		if (item.fields.type == 'mp3'){
			$('#song_table').append('<tr class="songs" id="song_'+item.pk+'" ><td ondblclick="play_song(\''+item.pk+'\', \'' + item.fields.type + '\', \'' + item.fields.letter + '\', \'' + item.fields.path + '\', \'' + item.fields.filename + '\')">' + item.fields.title + '</td>' +
			'<td>' + item.fields.length + '</td>');
		}
	})
	$('#albums').append('</table>');
}

function play_song(song_id, type, letter, path, song) {
	$('.songs').css('background', '#F7F7F7').css('color', '#555555')
	$('#song_' + song_id).css('background', '#7FAD35').css('color', '#ffffff')
	var destiny = "/static/music/"+letter+"/"+path+"/"+song;
	$("#jquery_jplayer_1").jPlayer("setMedia", {
		'mp3': destiny,
	});
	$("#jquery_jplayer_1").jPlayer("play", 0);
}
