var graphdata = [];
var ds;
$('#simloading').hide();
$('#graphloading').hide();
$('#ajaxloading').hide();
var datasetDiv = $('#dataset');
var dataset;
var targetId;
var t;
var lastid;
var lastscore;
var vector;
var simcounter = 0;

$(document).ready(function() {
    dataset = getUrlVars().dataset;
    targetId = getUrlVars().id;
    showResult(targetId);
    dataSet();

});

$("#dataset")
    .change(function() {
        var str = "";
        $("#dataset option:selected").each(function() {
            str += $(this).text() + " ";
        });
        $('#bio2vecgraph').empty();
        $('#accordion-1').empty();
        $('#entity-details').empty();
        $('#sim').empty();
    })
    .change();

$(function() {


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
                    //alert(data.lenght);
                    response($.map(data, function(item) {

                        return {
                            label: "<div style='padding-bottom: 20px'><b>" + item[0] + "</b>(dataset:" + item[2] + ")</div>",
                            value: item[0],
                            desc: item[1],
                            _data: item[3],
                            _dataset: item[2],
                            _vector: item[4]
                        }

                    }));
                }
            });
        },
        select: function(event, element) {
            dataset = element.item._dataset;
            showResult(element.item._data);
            //getSimGraph(element.item._vector);
            //showSim(element.item._dataset, element.item._vector);
        }

    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append(item.label)
            .appendTo(ul);
    };
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

function getGraph() {
    //alert("all dataset")
    var lastGraphId;
    var getmore = false;

    $.ajax({
        url: 'http://localhost:19000/graph.groovy?term=' + dataset,
        dataType: "json",
        success: function(data) {

            $.each(data, function() {
                lastGraphId = this._source.id;
                //alert(this._source.id);
                //alert("lastid="+lastGraphId)
                var polt = {
                    "pca_x": parseFloat(this._source.pca_x),
                    "pca_y": parseFloat(this._source.pca_y),
                    "id": this._source.id,
                    "name": this._source.name[0],
                    "entity": this._source.entity_type,
                    "_id": this._id
                };
                graphdata.push(polt);
            });
            graph(graphdata);

            if (data.length == 10000) {
                getmore = true;
                getMore();
            }
        },
        error: function(data) {
            console.log("error");
        }
    });

    function getMore() {

        //alert("in while");
        $.ajax({
            url: 'http://localhost:19000/graph.groovy?term=' + dataset + '&sa=' + lastGraphId,
            dataType: "json",
            success: function(data) {

                $.each(data, function() {
                    lastGraphId = this.id;
                    var polt = {
                        "pca_x": parseFloat(this._source.pca_x),
                        "pca_y": parseFloat(this._source.pca_y),
                        "id": this._source.id,
                        "name": this._source.name[0],
                        "entity": this._source.entity_type,
                        "_id": this._id
                    };
                    graphdata.push(polt);
                });
                graph(graphdata);


            },
            error: function(data) {
                console.log("error");
            }
        });
    }

}

function getSimGraph(model_factor) {

    graphdata = [];
    var lastGraphId;
    var getmore = false;
    $('#bio2vecgraph').empty();
    factor = model_factor.replace(/\s*\d+\|/g, ',').replace(/^,/, '');
    vector = factor;

    $.ajax({
        url: 'http://localhost:19000/simgraph.groovy?dataset=' + dataset + '&vector=' + vector,
        beforeSend: function() {
            $('#graphloading').show();
        },
        complete: function() {
            $('#graphloading').hide();
        },
        dataType: "json",
        success: function(data) {

            $.each(data, function() {
                $.each(this, function() {
                    var plotname;
                    this[0] == "no_name" ? plotname = this[1] : plotname = this[0][0];
                    var polt = {
                        "pca_x": parseFloat(this[3]),
                        "pca_y": parseFloat(this[4]),
                        "id": this[1],
                        "name": plotname,
                        "entity": this[2],
                        "_id": this[5]
                    };
                    graphdata.push(polt);
                });
            });
            graph(graphdata);
        },
        error: function(data) {
            console.log("error");
        }
    });
}


function dataSet() {

    $.ajax({

        url: 'http://localhost:19000/dataset.groovy?term=all',
        dataType: "json",

        success: function(data) {
            //alert(data);
            console.log("dataset" + data);
            $.map(data, function(item) {
                //console.log("hello"+item._source.dataset_name);
                //alert(item._source.dataset_name)
                $('#dataset').append($('<option>', {
                    value: item._source.dataset_name,
                    text: item._source.dataset_name
                }));

            });

        },
        error: function(data) {
            console.log("Dataset error");



        }


    })

}

function graph(data) {

    $('#bio2vecgraph').empty();
    var margin = {
            top: 50,
            right: 200,
            bottom: 50,
            left: 50
        },
        legendWidth = 1200,
        outerWidth = 900,
        outerHeight = 450,
        width = outerWidth - margin.left - margin.right,
        height = outerHeight - margin.top - margin.bottom;

    var padding = 0;
    var currentTransform = null;
    var legendData = [];
    //scale

    var x = d3.scaleLinear()
        .domain(d3.extent(data, function(d) {
            return d.pca_x;
        }))
        .range([padding, width - padding])
        .nice();

    var y = d3.scaleLinear()
        .domain(d3.extent(data, function(d) {
            return d.pca_y;
        }))
        .range([height, 0])
        .nice();

    var zoom = d3.zoom()
        .scaleExtent([0, 500])
        .translateExtent([
            [-width * 2, -height * 2],
            [width * 2, height * 2]
        ])
        .on("zoom", zoomed);

    var color = d3.scaleOrdinal(d3.schemeCategory10)
            .domain(["gene", "disease", "phenotype", "target","mesh", "gene_function", "chemical"]);

    var tip = d3.tip()
        .attr("class", "d3-tip")
        .offset([-10, 0])
        .html(function(d) {
            return "name: " + d.name + "<br>" + "id : " + d.id;
        });

    //chart
    var chart = d3.select('#bio2vecgraph')
        .append('svg:svg')
        .attr('width', legendWidth)
        .attr('height', outerHeight)
        .attr("fill", "gray")
        .attr('class', 'chart')
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + " )")
        .call(zoom);

    chart.call(tip);

    chart.append("rect")
        .attr("width", width)
        .attr("height", height);



    var xAxis = d3.axisBottom(x).tickSize(-height);

    var x_axis = chart.append('g')
        .attr('transform', 'translate(0,' + height + ')')
        .attr('class', 'x axis')
        .call(xAxis);

    var yAxis = d3.axisLeft(y).tickSize(-width);

    var y_axis = chart.append('g')
        .attr('transform', 'translate(0,0)')
        .attr('class', 'y axis')
        .call(yAxis)


    var objects = chart.append("svg")
        .classed("objects", true)
        .attr("width", width)
        .attr("height", height);

    var dots = objects.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("cx", function(d) {
            return x(d.pca_x);

        })
        .attr("cy", function(d) {
            return y(d.pca_y);

        })
        .attr("fill", function(d) {
            return entityCol(d.entity, d._id, d.name);
        })
        .attr("r", 3)
        .on("mouseover", tip.show)
        .on("mouseout", tip.hide);
    //add legand
    var legendSpace = 20;
    legendData.forEach(function(d, i) {

        chart.append("circle")
            .attr("r", 3)
            .attr("cx", width + (margin.bottom / 2) + 5)
            .attr("cy", (legendSpace / 2) + i * legendSpace)
            .attr("fill", function() { 
                return d.color;
            });

        chart.append("text")
            .attr("x", width + (margin.bottom / 2) + 13) // space legend
            .attr("y", ((legendSpace / 2) + i * legendSpace)+5)
            .attr("class", "legend") // style the legend
            .style("fill", function() { 
                return "#3d3d3d";
            })
            .text((d.entity.replace('http://bio2vec.net/ontology/', '')).substring(0, 50));
    });



    function zoomed() {

        x_axis.call(xAxis.scale(d3.event.transform.rescaleX(x)));
        y_axis.call(yAxis.scale(d3.event.transform.rescaleY(y)));


        // re-draw circles using new x-axis & y-axis 
        var new_y = d3.event.transform.rescaleY(y);
        dots.attr("cy", function(d) {
            return new_y(d.pca_y);
        });
        var new_x = d3.event.transform.rescaleX(x);
        dots.attr("cx", function(d) {
            return new_x(d.pca_x);
        });

        function transform(d) {
            return "translate(" + d3.event.transform.rescaleX(x) + "," + d3.event.transform.rescaleY(y) + ")";

        }


    }

    function entityCol(entity, _id, name) {

        if (_id == targetId) {
            var legEntity = {

                "entity": name,
                "color": "#FF0000"
            };
            legendData.push(legEntity);
            return "#FF0000";
        }

        else {
            var found = false;
            $.each(legendData, function() {
                if (this.entity == entity) {
                    found = true;
                    //break;

                }

            });
            if (!found) {
                var legEntity = {

                    "entity": entity,
                    "color": color(entity.replace('http://bio2vec.net/ontology/', ''))
                };
                legendData.push(legEntity);
            }
            return color(entity.replace('http://bio2vec.net/ontology/', ''));
        }
    }

}



function showMore() {
    $('#simmore').remove();
    $.ajax({

        url: 'http://localhost:19000/sim.groovy?vector=' + vector + '&dataset=' + dataset + '&sa=' + lastid + '&sc=' + lastscore,
        dataType: "json",

        success: function(data) {
            //console.log("success");
            //console.log(data.length);

            var simHtml = '<ul class="media-list media-list-divider">'
            $.each(data, function() {
                $.each(this, function() {
                    lastid = this[1];
                    lastscore = this[3];
                    //console.log(lastid);
                    //console.log(lastscore);
                    simcounter = simcounter + 1;
                    if (this[0][0] == "no_name") {
                        simHtml = simHtml + '<li class="media flexbox"><div><div class="media-heading"><span style="padding-right:10px;" >' + simcounter + ')</span><a class="text-success" onclick="showResult(' + this[4] + ');return false;" href="">' + this[1] + '</a></div></div></li>'
                    } else {
                        simHtml = simHtml + '<li class="media flexbox"><div><div class="media-heading"><span style="padding-right:10px;" >' + simcounter + ')</span><a class="text-success" onclick="showResult(' + this[4] + ');return false;" href="">' + this[0][0] + '</a></div><div class="font-13 text-light">' + this[1] + '</div></div></li>'

                    }
                });
            });
            simHtml = simHtml + '<li class="media flexbox" id="simmore"><div><div class="media-heading"><button class="btn btn-outline-info btn-fix btn-block" onclick="showMore();"> Show More</button></div></div></li>'
            simHtml = simHtml + '</div>';
            $('#sim').append(simHtml);


        },
        error: function(data) {
            console.log("similarity error");
            //console.log(data);

        }


    });
}

function showSim(ds, model_factor) {
    $('#sim').empty();
    simcounter = 0;
    var simDiv = $('#sim');
    dataset = ds;


    factor = model_factor.replace(/\s*\d+\|/g, ',').replace(/^,/, '');
    vector = factor;
    $.ajax({

        url: 'http://localhost:19000/sim.groovy?vector=' + factor + '&dataset=' + dataset,
        beforeSend: function() {
            $('#simloading').show();
        },
        complete: function() {
            $('#simloading').hide();
        },
        dataType: "json",

        success: function(data) {

            var simHtml = '<ul class="media-list media-list-divider">'
            $.each(data, function() {
                $.each(this, function(i) {
                    if (i > 0) {
                        lastid = this[1];
                        lastscore = this[3];
                        //console.log(lastid);
                        //console.log(lastscore);
                        simcounter = simcounter + 1;
                        if (this[0][0] == "no_name") {
                            simHtml = simHtml + '<li class="media flexbox"><div><div class="media-heading"><span style="padding-right:10px;" >' + simcounter + ')</span><a class="text-success" onclick="showResult(' + this[4] + ');return false;" href="">' + this[1] + '</a></div></div></li>'
                        } else {
                            simHtml = simHtml + '<li class="media flexbox"><div><div class="media-heading"><span style="padding-right:10px;" >' + simcounter + ')</span><a class="text-success" onclick="showResult(' + this[4] + ');return false;" href="">' + this[0][0] + '</a></div><div class="font-13 text-light">' + this[1] + '</div></div></li>'

                        }
                    }
                });
            });
            simHtml = simHtml + '<li class="media flexbox" id="simmore"><div><div class="media-heading"><button class="btn btn-outline-info btn-fix btn-block" onclick="showMore();"> Show More</button></div></div></li>'
            simHtml = simHtml + '</div>';
            $('#sim').append(simHtml);


        },
        error: function(data) {
            console.log("similarity error");
            //console.log(data);

        }


    });



}

function showResult(j) {

    targetId = j;
    $('#accordion-1').empty();
    $('#entity-details').empty();

    $.ajax({

        url: 'http://localhost:19000/SearchId.groovy?term=' + targetId + "&dataset=" + dataset,
        dataType: "json",

        success: function(data) {

            $.each(data, function() {
                console.log(this);
                details = this;
                //alert((details._source.entity_type).replace('http://bio2vec.net/ontology/', ''));
                //$('<div class="ibox-title">Similar Entities</div>').appendTo("#entity-details");
                if (details._source.name[0] == "no_name") {

                    $('#entity-details').append($('<div class="ibox-title">ID:' + details._source.id + '</div>'));
                } else {

                    $('#entity-details').append($('<div class="ibox-title">Name:' + details._source.name[0] + '</div>'));
                }
                if (details._source.name.length > 1) {
                    var synonym = '<div class="p-3 bg-primary-50 mt-3"><ul class="media-list media-list-divider">';


                    $.each(details._source.name, function(i) {
                        if (i > 0) {
                            synonym = synonym + '<li style="padding-left: 20px;">' + this + '</li>'
                        }
                    });


                    synonym = synonym + '</ul></div>'

                    var synonymliHtml = '<li class="list-group-item"><a class="text-success" data-toggle="collapse" href="#faq1-2">Synonym<i class="fa fa-angle-down"></i></a><div class="collapse show" id="faq1-2">' + synonym + '</div></li>'
                    $('#accordion-1')
                        .append($('<ul class="list-group list-group-divider list-group-full faq-list" />')
                            .append(synonymliHtml)
                        );
                }
                
                $('<p class="font-strong"><span class="font-strong" style="color: #18c5a9;  padding-right: 20px;">Dataset name :</span>' + details._source.dataset_name + '</p>').appendTo("#accordion-1");
                $('<p class="font-strong"><span class="font-strong" style="color: #18c5a9;  padding-right: 20px;">entity_type :</span>' + (details._source.entity_type).replace('http://bio2vec.net/ontology/', '') + '</p>').appendTo("#accordion-1");
                $('<p class="font-strong"><span class="font-strong" style="color: #18c5a9;  padding-right: 50px;">ID :</span><a  href="' + details._source.id + '" target="_blank">' + details._source.id + '</a></p>').appendTo("#accordion-1");



                factor = details._source['@model_factor'].replace(/\s*\d+\|/g, ',').replace(/^,/, '');
                var res = factor.split(',');
                var factorHtml = '<div class="p-3 bg-primary-50 mt-3">'
                var i = 0
                $.each(res, function() {
                    i = i + 1;
                    factorHtml = factorHtml + '<span style="padding-right: 20px; width:20px;">' + this + '</span>';
                    if (i == 7) {
                        factorHtml = factorHtml + '</br>';
                        i = 0;
                    }

                });
                factorHtml + '</div>';
                var liHtml = '<li class="list-group-item"><a class="text-success" data-toggle="collapse" href="#faq1-1">Vector<i class="fa fa-angle-down"></i></a><div class="collapse show" id="faq1-1">' + factorHtml + '</div></li>'
                $('#accordion-1')
                    .append($('<ul class="list-group list-group-divider list-group-full faq-list" />')
                        .append(liHtml)
                    );

            });

            showSim(details._source.dataset_name, details._source['@model_factor']);
            getSimGraph(details._source['@model_factor']);


        },
        error: function(data) {
            console.log("error");



        }


    })

}
