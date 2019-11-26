var searchData = [];
var datasetArray=[];
$('#ajaxloading').hide();
var term;

$(document).ready(function() {
    term = getUrlVars().term;
    showResult();

});

$("#restSearch").autocomplete({
    minLength: 0,
    source: function(request, response) {
        $.ajax({
            url: 'http://localhost:19000/detailedSearch.groovy?term=' + request.term,
            beforeSend: function() {
                $('#ajaxloading').show();
            },
            complete: function() {
                $('#ajaxloading').hide();
            },
            dataType: "json",
            success: function(data) {
                response($.map(data, function(item) {
                    //console.log(item)
                    return {
                        label: "<div style='padding-bottom: 20px'><b>" + item[0] + "</b>   ID:" + item[4] + "(dataset:" + item[2] + ")</div>",
                        value: item[0],
                        _data: item[3],
                        _dataSet: item[2]
                    }
                }));
            }
        });
    },
    select: function(event, element) {
        window.location.replace("Bio2VecSearch.html?id=" + element.item._data + "&dataset=" + element.item._dataSet);
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

            term=$("#restSearch").val();
            showResult();
            return false;
            //window.location.replace("detailedSearch.html?term=" + $("#restSearch").val());
        }
    }
});



function getUrlVars() {
    var vars = [],
        hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }

    return vars;
}

function showResult() {

    searchData = [];

    $.ajax({
        url: 'http://localhost:19000/detailedSearch.groovy?term=' + term,
        beforeSend: function() {
            $('#ajaxloading').show();
        },
        complete: function() {
            $('#ajaxloading').hide();
        },
        dataType: "json",
        success: function(data) {
            //console.log(data);
            $.each(data, function() {

                var result = {
                    "id": this[1],
                    "name": this[0],
                    "dataset": this[2],
                    "_id": this[3]

                };
                //console.log(result);
                searchData.push(result);
                 datasetArray.push(this[2]);
                $.unique(datasetArray);
            });
            showDataSet();
        },
        error: function(data) {
            console.log("error");
        }
    });
}

function showDataSet() {

    $("#dataset").empty();


    $.ajax({

        url: 'http://localhost:19000/dataset.groovy?term=all',
        dataType: "json",

        success: function(data) {
            //alert(data);
            console.log("dataset" + data);
            $.map(data, function(item) {
                if ($.inArray( item._source.dataset_name, datasetArray)!=-1){

                    var resulthtml = '<li class="media list-item">\
                                            <div class="media-body d-flex">\
                                                <div class="flex-1">\
                                                    <h5 class="media-heading">\
                                                    <a onclick="showDataSetResult(\'' + item._source.dataset_name + '\');" href="javascript:void(0)">' + item._source.dataset_name + '</a>\
                                                    </h5>\
                                                    <p class="font-13 text-light mb-1">' + item._source.description + '</p>\
                                                </div>\
                                            </div>\
                                        </li>';

                    $("#dataset").append(resulthtml);
                }
                

            });
            showDataSetResult(datasetArray[0]);
        },
        error: function(data) {
            console.log("Dataset error");



        }


    });

    




}

function showDataSetResult(dataSetName) {
    $('#result').empty();
    $.each(searchData, function() {
        if (dataSetName==this.dataset){
            var resulthtml = '<li class="media">\
                            <div class="media-body d-flex">\
                               <div class="flex-1">\
                                <h8 class="media-heading"> <a href="Bio2VecSearch.html?id=' + this._id + '&dataset=' + this.dataset+'" target="_blank">' + this.name + '</a></h8>\
                                 <p class="font-11 text-light mb-1">' + this.id+ '</p></div> </div></li>';
        $('#result').append(resulthtml);
        }
        
    });
}
