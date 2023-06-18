$(function(e) {
	
	$('#blogMemoryTable').DataTable({
		order: [[2, 'desc']],
	});
	
	$('#example').DataTable();
	
	$('#memoryTable').DataTable({
		order: [[3, 'desc']],
	});

	//______Select2 
	$('.select2').select2({
        minimumResultsForSearch: Infinity
	});
	
} );
