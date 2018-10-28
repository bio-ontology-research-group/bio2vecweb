var datasetDiv = $('#dataset');
var searchData = [];
var datasetArray=[];
$('#ajaxloading').hide();
var term;

$(document).ready(function() {
    term = getUrlVars().term;
    showResult();

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
        url: '/api/bio2vec/search/?label=' + term,
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

            });
            //graph(graphdata);
            showdetailed();
        },
        error: function(data) {
            console.log("error");
        }
    });
}

function showdetailed() {

    $("#1").empty();


    $.ajax({

        url: 'http://localhost:19000/dataset.groovy?term=all',
        dataType: "json",

        success: function(data) {
            //alert(data);
            console.log("dataset" + data);
            $.map(data, function(item) {

                var resulthtml = '<div class="col-md-4"><div class="ibox shadow-wide">\
        <div class="ibox-body text-center" id="' + item._source.dataset_name.toString() + '">\
        <h5 class="font-strong">' + item._source.dataset_name + '</h5>\
        <div class="text-muted mb-4">' + item._source.description + '</div>\
        <div class="ibox-fullwidth-block p-3 bg-primary text-white d-flex align-items-center justify-content-center">\
        </div></div></div></div>';

                //var resulthtml ='<div class="row" id="' + item._source.dataset_name.toString() + '"></div>'

                $("#1").append(resulthtml);

            });
            $.each(searchData, function() {
        var resulthtml = '<div class="flexbox-b mb-3" -data="' + this._id + '">' + this.name + this.id + '</div>';
        $('#'+this.dataset).append(resulthtml);
    });

        },
        error: function(data) {
            console.log("Dataset error");



        }


    });

    




}




/*var datasetDiv = $('#dataset');
$('#ajaxloading').hide();
//var root='https://restcountries.eu/rest/v2/name/'
$("#restSearch").autocomplete({
    minLength: 0,
    source: function(request, response) {
        $.ajax({
            url: 'http://localhost:19000/search.groovy?term=' + request.term,
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
            var resulthtml = '<div class="col-md-4">\
                                <div class="ibox shadow-wide">\
                                    <div class="ibox-body text-center">\
                                        <h3 class="font-strong">BUSINESS</h3>\
                                        <div class="text-muted mb-4">For Starter Business</div>\
                                        <div class="ibox-fullwidth-block p-3 bg-primary text-white d-flex align-items-center justify-content-center">\
                                            <h1 class="font-strong mb-0 mr-2"><sup>$</sup>45</h1>\
                                            <span>/ mo</span>\
                                        </div>\
                                        <div class="py-5">\
                                            <div class="flexbox-b mb-3"><i class="la la-check mr-3 font-18"></i>125 GB space</div>\
                                            <div class="flexbox-b mb-3"><i class="la la-check mr-3 font-18"></i>5 websites</div>\
                                            <div class="flexbox-b mb-3"><i class="la la-check mr-3 font-18"></i>3 email address</div>\
                                            <div class="flexbox-b mb-3"><i class="la la-check mr-3 font-18"></i>SSH access</div>\
                                            <div class="flexbox-b mb-3"><i class="la la-check mr-3 font-18"></i>Unlimited Users</div>\
                                            <div class="flexbox-b mb-3 text-muted"><i class="la la-times-circle mr-3 font-18"></i>Advanced settings</div>\
                                        </div>\
                                        <button class="btn btn-primary btn-rounded btn-air">PURCHASE</button>\
                                    </div>\
                                </div>\
                            </div>'



            $("#result").append(resulthtml);
            //window.location.replace("Bio2VecSearch.html");



        }
    }
    else{
         $("#result").empty();

    }
});
*/
