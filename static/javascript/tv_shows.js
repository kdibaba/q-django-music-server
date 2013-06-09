$(document).ready(function() {
	drive_shows = $("#drive_shows")
    if (drive_shows.length) {
    	$("#drive_list").fadeOut('slow');
    }
    else {
    	$("#show_hide_drives_list").fadeOut('slow')
    }
	$(".delete_option").css('display', 'none');
});

function show_drives() {
	$("#drive_list").fadeIn('slow');
	
}

function hide_drives() {
	$("#drive_list").fadeOut('slow');
	
}

function show_delete_option() {
	$(".delete_option").css('display', '');
}

function hide_delete_option() {
	$(".delete_option").css('display', 'none');
}

function delete_episode( id ) {
	drive = $("#id_drive_letter").val();
	if (drive != ""){
		jQuery.ajax({
			url: "/delete_episode/?episode_id="+id+"&drive="+drive,
			async:   false
		});
		$("#"+id).remove();
	}
	else {
		alert('You need a Drive Letter Fool.')
	}
}	
