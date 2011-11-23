$(document).ready(function(){

    //HANDLE url changes
    $(window).bind( 'hashchange', function(){handle_hash()});
    handle_hash();

    //HANDLE jPlayer size
	//var new_width = $(window).width() - 316
	//$('.jp-mute').css('margin-left', new_width+'px')
    //$(window).resize(function() {
	//  var new_width = $(window).width() - 316  
	//  $('.jp-mute').css('margin-left', new_width+'px')
	//});
	
	$("#menu_albums").hoverIntent({
		over: show_menu_albums,
		timeout: 500,
		out: hide_menu_albums
	});
	
	$("#menu_artists").hoverIntent({
		over: show_menu_artists,
		timeout: 500,
		out: hide_menu_artists
	});
	
	$("#menu_add_music").hoverIntent({
		over: show_menu_add,
		timeout: 500,
		out: hide_menu_add
	});
	
	$("#menu_search").hoverIntent({
		over: show_menu_search,
		timeout: 500,
		out: hide_menu_search
	});

	function show_menu_albums(){$('.nav_button_albums').slideDown('fast');}
	function hide_menu_albums(){ $('.nav_button_albums').slideUp('fast')}
	function show_menu_artists(){$('.nav_button_artists').slideDown('fast')}
	function hide_menu_artists(){$('.nav_button_artists').slideUp('fast')}
	function show_menu_add(){$('.nav_button_add').slideDown('fast')}
	function hide_menu_add(){$('.nav_button_add').slideUp('fast')}
	function show_menu_search(){$('.nav_button_search').slideDown('fast')}
	function hide_menu_search(){$('.nav_button_search').slideUp('fast')}

    $("#searchBox").keyup(function(){
	    if (event.keyCode == 13){
	    	location.href='/#/search/'+$("#searchBox").val();
	    }
        });

	   
    //$('.nav_button_add').hover( function(){$('.nav_button_add').show(); }, function(){$('.nav_button_add').hide(); });
    //$('.nav_button_artists').hover( function(){$('.nav_button_artists').show(); }, function(){$('.nav_button_artists').hide(); });
    //$('.nav_button_albums').hover( function(){$('.nav_button_albums').show(); }, function(){$('.nav_button_albums').hide(); });
    //$('.nav_button_search').hover( function(){$('.nav_button_search').show(); }, function(){$('.nav_button_search').hide(); });
	  
	PLAYLIST = new jPlayerPlaylist({
		jPlayer: "#jquery_jplayer_1",
		cssSelectorAncestor: "#jp_container_1"
	},  [], {
		swfPath: "/static/javascript/",
		supplied: "oga, mp3",
		solution: "flash, html"
	});
	$(document.documentElement).keyup(function (event) {
		if (event.keyCode == 32) {
    		if(NOW_PLAYING){
    		    PLAYLIST.pause();
    			NOW_PLAYING = false
    		}
    		else{
	    		PLAYLIST.play();
	    		NOW_PLAYING = true
		  	}
		}
		else if (event.keyCode == 78) {
    		if(PLAYLIST){
    		    PLAYLIST.next();
    		}
		}
		});
	
	ARTISTS_HOR = parseInt($(window).width()/300);
	ARTISTS_VERT = parseInt($(window).height()/230);
	ARTISTS_COUNT = ARTISTS_HOR * ARTISTS_VERT;
	ARTISTS_CONTENT = ''
	ARTISTS_LETTER = ''
	
	$(window).resize(function() {
		ARTISTS_HOR = parseInt($(window).width()/300);
		ARTISTS_VERT = parseInt($(window).height()/230);
		ARTISTS_COUNT = ARTISTS_HOR * ARTISTS_VERT;
		$('#artists').css('width', ARTISTS_HOR*275+'px')
		});
});