function debounce(func, delay) {
    var timeout;
    return function() {
        var args = arguments;
        if (timeout)
            clearTimeout(timeout)
        timeout = setTimeout(function() {
            func.apply(null, arguments);
        }, delay || 100);
        return timeout;
    };
}

function sidebar(){
	$('[data-toggle=offcanvas]').click(function() {
	  	$(this).toggleClass('visible-xs text-center');
	    $(this).find('i').toggleClass('glyphicon-chevron-right glyphicon-chevron-left');
	    $('.row-offcanvas').toggleClass('active');
	    $('#lg-menu').toggleClass('hidden-xs').toggleClass('visible-xs');
	    $('#xs-menu').toggleClass('visible-xs').toggleClass('hidden-xs');
	    $('#btnShow').toggle();
	});
}


$(document).on('ready', function(){

	sidebar();

	function createSelect(data){
		var select = document.createElement('select');
		var option_base = document.createElement('option');
		for(var i=0;i<data.length;i++){
			option = option_base.cloneNode();
			option.value = data[i][1];
			option.text = data[i][0];
			select.appendChild(option);			
		}
		return select;
	}


	$.get('/acts.json')
		.then(function(data){
			$('#act-name').typeahead({ 
				items:10,  
				showHintOnFocus: true, 
				source: data.acts.map(function(a){
					return a[0];
				}),
				appendAfter: $('.sidebar-offcanvas'),
				afterSelect: function(){
					this.$element.parents('.form-group').next().find('input, select').focus();
				}
			});
		});


	function appendExpandControl(legislation){
		var topLevel = $('.top-level', legislation);
		if( topLevel.height() > topLevel.parent().height()){
			$('<div/>').addClass('expand')
			.appendTo(topLevel.parent())
			.on('click', function(){
				legislation.toggleClass('expanded');
			})
		}
	}

	function updateReferences(){
		var ids = $('.legislation *[id]').map(function(){
			return this.id;
		}).toArray();
		if(ids.length){
			$.get('/find_references/'+ids.join(';'))
				.then(function(result){
					$('.reference_list').html('')
					var lis = result.references.map(function(r){
						return $('<li/>').append($('<a/>').attr('href', r[0]).text(r[1]));
					})
					$('.reference_list').append(lis);
				});
		}
	}

	function updateLegislation(response){
		var result = $(response).find('.result');
		if(result.length){
			result.appendTo('.legislation_viewer');
			$('.legislation_finder .error').hide();
			appendExpandControl($('.legislation'));
			updateReferences();
		}else{
			$('.legislation_finder .error').show();
		}
	}

	var serial;
	function hasChanged(){
		var new_serial = $('.legislation_finder').serialize();
		console.log(new_serial, serial)
		if(new_serial !== serial){
			serial = new_serial;
			return true;
		}
		return false;
	}


	function getActs(){
		var act = $('#act-name').val().toLowerCase().replace(/ /g, ''),
			find = $('#find').val(),
			value = $('#value').val(),
			url = '/act/';
		url += act+'/';
		if(hasChanged() && value){
			if(find !== 'section'){
				url += find+'/';
			}
			url += value;
			$.get(url)
				.then(function(response){
					$('.result').remove();
					return response;
				})
				.then(updateLegislation);
		}
	}

	function getQuery(){
		var value = $('#query').val();
		if(hasChanged() && value){
			$.get('/full_search/'+value)
				.then(updateLegislation);
		}
	}

	function handleLink(event){
		var link = $(event.target).attr('href');
		$.get(link)
			.then(updateLegislation);
		return false;
	}




	$('.legislation_finder').on('change', '#type', function(){
		var val = $(this).val();
		$('.legislation_finder').find('.switchable').hide();
		$('.switchable').each(function(){
			if($(this).hasClass('visible-'+val)){
				$(this).show();
			}
		});
	});

	$('.legislation_finder').on('change', '#find', function(){
		$('#valueLabel').text($('#find').find('option:selected').text());
	});
	$('#find').trigger('change');
	$('.legislation_finder').on('change keyup', '#act-name, #find, #value', debounce(getActs, 300));
	$('.legislation_finder').on('change keyup', '#query', debounce(getQuery, 300));

	$('#find, #type').trigger('change');

	$('.legislation_viewer').on('click', 'a', handleLink);

});