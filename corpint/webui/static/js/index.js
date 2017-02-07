(function() { 

	var $approval_buttons = $('#to_approve .btn');
	$approval_buttons.click(function(e) { 
		e.preventDefault();
		var data = {
			action: $(this).data('action'),
			left_uid: $(this).parent().data('leftuid'),
			right_uid: $(this).parent().data('rightuid')
		};
	    $.post("/update", data, function() {
	        location.reload();
	    });
	});

	var $review_links = $('#to_review a');
	$review_links.click(function(e) { 
		e.preventDefault();
		var data = {
			action: $(this).data('action'),
			left_uid: $(this).parent().data('leftuid'),
			right_uid: $(this).parent().data('rightuid')
		};
	    $.post("/update", data, function() {
	        location.reload();
	    });
	});
	
})();