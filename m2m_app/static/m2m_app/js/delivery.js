$('document').ready(function() {
	var map;
	let markers = [];
	var codeSDEC = null
	var image = ''
    const TOTAL = $('#total').data('total')
	var DELIVERY_COST = 0
	var CITY_ID = null
	var CDEK_ADDRESS = '-'

	var markerIcon = {
	  url: 'http://image.flaticon.com/icons/svg/252/252025.svg',
	  scaledSize: new google.maps.Size(80, 80),
	  origin: new google.maps.Point(0, 0),
	  anchor: new google.maps.Point(32,65)
	};

	function initMap(zoom=3, lat=62.110960, lng=99.005391) {
		map = new google.maps.Map(document.getElementById("map"), {
          zoom: zoom,
          center: { lat: lat, lng: lng },
        });
		image = "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png";
	}
	// Adds a marker to the map and push to the array.
	function addMarker(location, lable, code) {
	  const marker = new google.maps.Marker({
		position: location,
		map: map,
		  lable: lable,
		  code: code,
			ico: image,

	  });
	  marker.attrSe = lable
	  marker.addListener("click", (lab = marker.lable) => {
		$('#address_cdek').text(marker.lable)
		  CDEK_ADDRESS = marker.lable
		  get_delivery_cost(CITY_ID)
		  codeSDEC = marker.code
	  });
	  markers.push(marker);
	}

	function addUserMarker(location, address) {
	  const marker = new google.maps.Marker({
		position: location,
		map: map,
		  lable: {
			color: "#006363"
		  },

		  icon: 'https://icons.iconarchive.com/icons/icons-land/vista-map-markers/48/Map-Marker-Marker-Inside-Azure-icon.png'	  });
	  markers.push(marker);
	  map.setCenter(location);
	  map.setZoom(13);
	}

	// Sets the map on all markers in the array.
	function setMapOnAll(map) {
	  for (let i = 0; i < markers.length; i++) {
		markers[i].setMap(map);
	  }
	}

	// Removes the markers from the map, but keeps them in the array.
	function clearMarkers() {
	  setMapOnAll(null);
	}

	// Shows any markers currently in the array.
	function showMarkers() {
	  setMapOnAll(map);
	}

	// Deletes all markers in the array by removing references to them.
	function deleteMarkers() {
	  clearMarkers();
	  markers = [];
	}

	initMap()

	function remoove_disabled(selector_ind) {
		let selector = $(selector_ind)
		selector.removeAttr("disabled")

	}

	function add_disabled(selector_ind) {
		let selector = $(selector_ind)
		selector.attr("disabled", true)

	}

	function get_delivery_cost(city_id){
		let url = $('#delivery_cost_url').data('delivery_cost_url')
		$.get(url, {'city_id': city_id}, function (data) {
			DELIVERY_COST = data['price']
			set_delivery_price(DELIVERY_COST)
			set_total(parseInt(TOTAL) + parseInt(DELIVERY_COST))
			pay_btn_switcher(true)
		})
	}

	function pay_btn_switcher(param) {
			if (param) {
				$('#pay-btn').attr('class', 'pay-btn-active');
				$('#pay-btn-lg').attr('class', 'pay-btn-active');
			} else{
				$('#pay-btn').attr('class', 'pay-btn');
				$('#pay-btn-lg').attr('class', 'pay-btn');
			}


	}

	function set_delivery_price(val){
		$('#delivery_price').text(`${val} руб.`)
		$('#delivery_price_lg').text(`${val} руб.`)
	}

	function set_total(val){
		$('#total').text(`${val} руб.`)
		$('#total_lg').text(`${val} руб.`)
	}

	$('#delivery_custom').change(function(event) {
		remoove_disabled('#delivery_custom_textarea')
		add_disabled('#city')
		set_delivery_price('-')
		set_total(TOTAL)
		$('#address_cdek').text('-')
	});

	$('#delivery_standard').change(function(event) {
		add_disabled('#delivery_custom_textarea')
		remoove_disabled('#city')
		set_delivery_price(DELIVERY_COST)
		set_total(parseInt(TOTAL) + parseInt(DELIVERY_COST))
		$('#address_cdek').text(CDEK_ADDRESS)

	});

	$('#delivery_custom_textarea').change(function (event) {
		if($('input:checked').attr('id') == "delivery_custom" && this.value.length > 0){
			pay_btn_switcher(true)
		}else pay_btn_switcher(false)
	})

	$('#city').blur(function(event) {
		let address = this.value
		let url = $('#parse_city_row_url').data('parse-city-row')
		$.get(url, {'address': address}, function(data) {
			console.log(data)
			deleteMarkers()
			CITY_ID = data['city_id']
			addUserMarker(data['user_point']['location'], )
			$.each(data['pvz'], function(i, el) {
				addMarker(el['location'], el['address'], el['code'])
			});
		});
	});

	function approve_delivery(data){
		let url = document.location.pathname
		$.post(url, data, function (data) {
			if (data['reverse']){
				let redirect_url = `${document.location.protocol}//${document.location.host}${data[['reverse']]}`
				console.log(redirect_url)
				document.location.href = redirect_url
			}
		})
	}

	$('#pay-btn').click(function(event) {
		if($('input:checked').attr('id') == "delivery_custom" && $('#delivery_custom_textarea').val().length > 0){
			let val = $('#delivery_custom_textarea').val()
			approve_delivery({'custom_delivery_message': val, 'delivery_type': 'CUSTOM_TYPE'})
		}else if($('input:checked').attr('id') == "delivery_standard"){
			approve_delivery({
				'address_sdek': CDEK_ADDRESS,
				'sdek_id': codeSDEC,
				'delivery_cost': DELIVERY_COST,
				'delivery_type': 'STANDARD_TYPE'
			})
		}else {
			pay_btn_switcher(false)
			alert('Заполните неоходимые поля')}
	})

	$('#pay-btn-lg').click(function(event) {
		if($('input:checked').attr('id') == "delivery_custom" && $('#delivery_custom_textarea').val().length > 0){
			let val = $('#delivery_custom_textarea').val()
			approve_delivery({'custom_delivery_message': val, 'delivery_type': 'CUSTOM_TYPE'})
		}else if($('input:checked').attr('id') == "delivery_standard"){
			approve_delivery({
				'address_sdek': CDEK_ADDRESS,
				'sdek_id': codeSDEC,
				'delivery_cost': DELIVERY_COST,
				'delivery_type': 'STANDARD_TYPE'
			})
		}else {
			pay_btn_switcher(false)
			alert('Заполните неоходимые поля')}
	})

	// $('#pay-btn').click(function(event) {
	// 	event.preventDefault()
	// });
});