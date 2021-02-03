$('document').ready(function() {

	function calculation_price(){
		let val = $('#count').val() * $( "input:checked" ).data('price') + ' руб.'
		$('#price').text(val)
	}

	if ($('#count').val() > 0 && $("input:checked")) {
			$('button[type=submit]').removeAttr("disabled")
			calculation_price()
		}

	$('#count').on('change', function(event) {
		if (this.value < 5){
			this.value = 5
		}
		if (this.value > 0) {
			$('button[type=submit]').removeAttr("disabled")
			calculation_price()
		} else {
			$('button[type=submit]').attr({
				disabled: '',})
				$('#price').text('0 руб.')
		};
		if (!(Number.isInteger(this.value))){
			$('#count').val(Math.round(this.value))
			calculation_price()
		}
		
	    });

	$('input[type=radio][name=tariff_pk]').change(function(event) {
		calculation_price()
	});
	// reset price after checked change
});
