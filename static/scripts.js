var row_timeouts = {};

function change_row(event){
	var row = event.target.closest('.show');
	row.classList.remove("done");
	row.classList.remove("error");
	row.classList.add("updating");

	var rowid = $(row).find('input#rowid');
	var date = $(row).find('input#date');
	var time = $(row).find('input#time');
	var showname = $(row).find('input#showname');
	var visitors = $(row).find('input#visitors');
	var vert = $(row).find('input#vert');

	var data = {rowid: rowid.val(), date: date.val(), time: time.val(), show_name: showname.val(), visitors: visitors.val(), vert: vert.val()};

	function success(got_data){
		console.log("Success");
		console.log(got_data);
		rowid.val(got_data['rowid']);
		row.classList.remove('updating');
		row.classList.remove('error');
		row.classList.add('done');
	}
	function fail(error){
		console.log("Fail");
		console.log(error);
		row.classList.remove('updating');
		row.classList.remove('done');
		row.classList.add('error');
	}
	console.log("Clearing timeout", row_timeouts[row])
	clearTimeout(row_timeouts[row]);
	row_timeouts[row] = setTimeout(function(){
	    console.log("Sending POST")
	    $.post("/add_row", data, success, 'json').fail(fail);
	}, 1000);

}
function delete_row(event){
	var row = event.target.closest('.show');
	var rowid = $(row).find('input#rowid');
	function success(got_data){
		console.log("Success");
		console.log(got_data);
		$(row).remove();
	}
	function fail(error){
		console.log("Fail");
		console.log(error);
		row.classList.remove('updating');
		row.classList.remove('done');
		row.classList.add('error');
	}
	var data = {rowid: rowid.val()};
	$.post("/delete_row", data, success, 'json').fail(fail);

}



$(document).ready(function (){
	$('.show input').on('change textInput input', change_row);
	$('.show button').click(delete_row);
});