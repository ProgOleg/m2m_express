$('document').ready(function() {

	function get_indi_entrepr_info(selector, obj, div_id){
		if (selector.val().length >= 10){
			let url = selector.data('ajax-url')
			let val = obj.value
			$.post(url, {'query': val}, function(data, textStatus, xhr) {
				if (data['entrepreneur_info']){
					for(let [key,val] of Object.entries(data['entrepreneur_info'])){$(`div#${div_id} input[name="${key}"]`).val(val)}
				}
			});
		};
	}

    //$("div.desc").hide();
    $("input[name$='select-tarif']").change(function() {
        $("#juridical_entrepreneur-form").hide();
        $("#individual_entrepreneur-form").hide();
        $("#physical-form").hide();
        $("#" + this.value).show();
        if (this.value == 'physical-form') {
        	$('#add').addClass('fiz-lico')
        }
        else{$('#add').removeClass('fiz-lico')}
    }).filter(function(){
        return this.checked;
    }).change();


	$('#entrepr_inn').change(function(event) {
		console.log('lets work!')
		get_indi_entrepr_info($('#entrepr_inn'), this, 'individual_entrepreneur-form')
	});	

	$('#juridical_entrepreneur').change(function(event) {
		console.log('lets work!')
		get_indi_entrepr_info($('#juridical_entrepreneur'), this, 'juridical_entrepreneur-form')
	});
	
});

