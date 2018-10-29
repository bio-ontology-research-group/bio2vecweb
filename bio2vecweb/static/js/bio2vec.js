$(document).ready(function() {
    $('#ajaxloading').hide();
    $("#restSearch").autocomplete({
	minLength: 0,
	source: function(request, response) {
            $.ajax({
		url: '/api/bio2vec/search?label=' + request.term,
		beforeSend: function() {
                    $('#ajaxloading').show();
		},
		complete: function() {
                    $('#ajaxloading').hide();
		},
		dataType: "json",
		success: function(data) {
		    console.log(data);
                    if (data.status == 'ok') {
			response($.map(data.result, function(item) {
			    var dataset_id = item['_type'].split('_')[1];
			    var data = item['_source'];
			    return {
				label: data['label'],
				id: data['id'],
				dataset_id: dataset_id
			    }
			}));
		    }
		}
            });
	},
	select: function(event, element) {
	    var item = element.item;
            window.location.replace('/bio2vec/details/' + item.dataset_id + '?iri=' + item.id);
	}
    }).autocomplete("instance")._renderItem = function(ul, item) {
	return $("<li>")
            .append("<div style='padding-bottom: 20px'><b>" + item.label + "</b></div>")
            .appendTo(ul);
    };

});
