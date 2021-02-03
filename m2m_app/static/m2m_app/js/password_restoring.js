$('document').ready(function(){

	$('#restoring_form').submit(function(event) {
		event.preventDefault();
		let username = this.username.value
		let url = $('#restoring_form').data('ajax-url')
		$.post(url, {'username': username}, function(data, textStatus, xhr) {
			$('#error').remove()
			let message = data['massage']['error']
			if(message){
				$('[name="username"]').after(`<p id="error" style="color: red">${message}</p>`)
			}
			else{
				$('#main_form').css({'display': 'none'});
				$('#mail_message').text(`Инструкция по восстановлению пароля успешно отправлена на указанную вами почту "${username}"`)
				$('#popapp_massage').css({'display': ''});
			}
		});
	});

})