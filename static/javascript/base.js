$(document).ready(function(){

	ARTISTS_HOR = parseInt(($(window).width()-200)/265);
	ARTISTS_VERT = parseInt(($(window).height()-200)/135);
	ARTISTS_COUNT = ARTISTS_HOR * ARTISTS_VERT;
	ARTISTS_CONTENT = ''
	ARTISTS_LETTER = ''
	ARTISTS_PAGE = ''

	ALBUMS_HOR = parseInt($(window).width()/220);
	ALBUMS_VERT = parseInt(($(window).height()-140)/200);
	ALBUMS_COUNT = ALBUMS_HOR * ALBUMS_VERT;
	ALBUMS_CONTENT = ''
	ALBUMS_LETTER = ''
	ALBUMS_YEAR = ''
	ALBUMS_PAGE = ''

	$('body').css('height',($(window).height()-80)+'px')		
	
	$('.redButton').click(function(){$('body').removeClass('theme_white').removeClass('theme_black').addClass('theme_red');set_theme('red');})
	$('.whiteButton').click(function(){$('body').removeClass('theme_red').removeClass('theme_black').addClass('theme_white');set_theme('white');})
	$('.blackButton').click(function(){$('body').removeClass('theme_white').removeClass('theme_red').addClass('theme_black');set_theme('black');})

	$(window).resize(function() {

		$('body').css('height',($(window).height()-80)+'px')	
		
		ARTISTS_HOR = parseInt(($(window).width()-200)/265);
		ARTISTS_VERT = parseInt(($(window).height()-200)/135);
		ARTISTS_COUNT = ARTISTS_HOR * ARTISTS_VERT;
		$('#artists').css('width', ARTISTS_HOR*265+'px')
		
		
		ALBUMS_HOR = parseInt($(window).width()/220);
		ALBUMS_VERT = parseInt(($(window).height()-140)/200);
		ALBUMS_COUNT = ALBUMS_HOR * ALBUMS_VERT;
		$('#albums').css('width', ALBUMS_HOR*200+'px')
		
		// Fix the jplayer dimensions on window resize;
		if ($('div.jp-progress')){$('div.jp-progress').css("width", $(window).width()-340+'px');}
		if ($('div.jp-time-holder')){$('div.jp-time-holder').css("width", $(window).width()-350+'px');}
		if ($('.jp-toggles')){$('.jp-toggles').css("left", $(window).width()/2+'px');}
		
		// If on an album page fix the height of the song table on window resize
		
		if ($('#song_table_wrapper')){
			var table_height = $("#song_table_wrapper").height();
			var content_height = $(window).height()-310;
			
			if (content_height < table_height) { 
				$('#song_table_wrapper').css('height', content_height+'px');
			}
			else {
				$('#song_table_wrapper').css('height', "")
				$('#song_table_wrapper').css('height', content_height+'px');
			}
		}
	})
	
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

});

function show_hide_admin() {
	$('#admin_pane').toggle('slow')
}


function set_theme(field){
	jQuery.ajax({
		url: "/set_theme/?query="+field,
		failure: function(){
			display_message_alert('Failed.', false);
		},
		async:   false
	});
}	