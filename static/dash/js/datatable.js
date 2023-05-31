$(function(e) {
	
	$('#blogMemoryTable').DataTable({
		order: [[2, 'desc']],
	});
	$('#example').DataTable();
	

	//______Select2 
	$('.select2').select2({
        minimumResultsForSearch: Infinity
	});
	
} );
