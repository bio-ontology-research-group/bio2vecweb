var datasetDiv = $('#dataset');
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
			return {
                            label: "<div style='padding-bottom: 20px'><b>" + item['_source']['label'] + "</b></div>"
			}
                    }));
		}
            }
        });
    },
    select: function(event, element) {
        window.location.replace("search.html?term=" + $("#restSearch").val());
    }
}).autocomplete("instance")._renderItem = function(ul, item) {
    return $("<li>")
        .append(item.label)
        .appendTo(ul);
};
$("#restSearch").keydown(function(event) {
    if (event.keyCode == 13) {
        if ($("#restSearch").val().length == 0) {
            event.preventDefault();
            return false;
        } else {

            window.location.replace("search.html?term=" + $("#restSearch").val());
        }
    }
});
