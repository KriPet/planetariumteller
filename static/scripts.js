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
	$.post("/add_row", data, success, 'json').fail(fail);
}
function delete_row(event){
	var row = event.target.closest('.show');
}



$(document).ready(function (){
	$('.show input').on('change textInput input', change_row);
	$('.show button').click(delete_row);
});