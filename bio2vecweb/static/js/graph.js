$(document).ready(function() {
    $("#restSearch").autocomplete({
	minLength: 0,
	source: function(request, response) {
            $.ajax({
		url: '/api/bio2vec/search?label=' + request.term + '&dataset=' + dataset,
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
			    var dataset_id = item['_index'].split('_')[1];
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

    function graph(data) {

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
            height = outerHeight - margin.top - margin.bottom,
	    r = 5;

	var padding = 0;
	var currentTransform = null;

	var types = new Set();
	data.forEach(function(d) {
	    types.add(d.type);
	});
	
	var x = d3.scaleLinear()
            .domain(d3.extent(data, function(d) {
		return d.x;
            }))
            .range([padding, width - padding])
            .nice();

	var y = d3.scaleLinear()
            .domain(d3.extent(data, function(d) {
		return d.y;
            }))
            .range([height, 0])
            .nice();

	var zoom = d3.zoom().on("zoom", zoomed);

	var color = d3.scaleOrdinal(d3.schemeCategory10)
            .domain(types);
	
	var tip = d3.tip()
            .attr("class", "d3-tip")
            .offset([-10, 0])
            .html(function(d) {
		return "name: " + d.label + "<br>" + "id : " + d.id;
            });

	// chart
	var chart = d3.select('#bio2vecgraph')
            .append('svg:svg')
            .attr('width', legendWidth)
            .attr('height', outerHeight)
            .attr("fill", "white")
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
		return x(d.x);

            })
            .attr("cy", function(d) {
		return y(d.y);

            })
            .attr("fill", function(d) {
		return color(d.type);
            })
            .attr("r", function(d) {
		if (d.id == targetId) return r * 2;
		return r;
	    })
            .on("mouseover", tip.show)
            .on("mouseout", tip.hide);
	
	//add legand
	var legendSpace = 20;
	var i = 0;
	types.forEach(function(d) {
	    chart.append("circle")
		.attr("r", r)
		.attr("cx", width + (margin.bottom / 2) + 5)
		.attr("cy", (legendSpace / 2) + i * legendSpace)
		.attr("fill", function() { 
                    return color(d);
		});

            chart.append("text")
		.attr("x", width + (margin.bottom / 2) + 13) // space legend
		.attr("y", ((legendSpace / 2) + i * legendSpace) + 5)
		.attr("class", "legend") // style the legend
		.style("fill", function() { 
                    return "#3d3d3d";
		})
		.text(d);
	    i++;
	});



	function zoomed() {

            x_axis.call(xAxis.scale(d3.event.transform.rescaleX(x)));
            y_axis.call(yAxis.scale(d3.event.transform.rescaleY(y)));


            // re-draw circles using new x-axis & y-axis 
            var new_y = d3.event.transform.rescaleY(y);
            dots.attr("cy", function(d) {
		return new_y(d.y);
            });
            var new_x = d3.event.transform.rescaleX(x);
            dots.attr("cx", function(d) {
		return new_x(d.x);
            });

            function transform(d) {
		return "translate(" + d3.event.transform.rescaleX(x) + "," + d3.event.transform.rescaleY(y) + ")";

            }


	}
    }

    graph(similars);
});

