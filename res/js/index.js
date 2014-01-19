	// Globals :(
	var linkedinMap = new LinkedinMap('linkedin-map-canvas');
	var coopMap = new CoopMap('coop-map-canvas');

	var infoWindow = new google.maps.InfoWindow();
	var infoWindowArray = new Array();

	// Ready function
	$(document).ready(function(){

		// Load the LinkedIn data
		$.ajax({
			url: "map-content/linkedIn-data/profiles.txt",
			isLocal: true,
			dataType: "json"
		})
		.done(function(data){
			console.log("AJAX for linkedIn profiles - Success!");
			console.log(data);
			linkedinMap.mapData = data;
			linkedinMap.generatePoints();
		})
		.fail(function(data){
			console.log("AJAX for linkedIn profiles - Fail!");
			console.log(data);
		})

		// Load the co-op data
		$.ajax({
			url: "map-content/coop-data/coop-profiles.txt",
			isLocal: true,
			dataType: "json"
		})
		.done(function(data){
			console.log("AJAX for co-op profiles - Success!");
			console.log(data);
			coopMap.mapData = data;
			coopMap.generatePoints();
		})
		.fail(function(data){
			console.log("AJAX for co-op profiles - Fail!");
			console.log(data);
		})

		// Hover for content tiles
		$('.tile').hover(function(){
			// Hover in
			console.log('hover in: ' + $(this));
			$(this).fadeTo(0);
		}, function(){
			// Hover out
			console.log('hover out: ' + $(this));
			$(this).fadeTo(1);
		});

		// Event listener for pop-ups
		var pbg = document.getElementById('popup-background');
		pbg.addEventListener("click", function(){hidePopup()}, false);

		// Escape key exits the
		$(document).keyup(function(evt){
			if(evt.keyCode == 27){
				hidePopup();
			}
		});

		// Set LocalSroll
		$("#splash").localScroll();
		$("#nav").localScroll();

		// When the user scrolls, we run the scrollBG function
		$(window).bind('scroll', function(){
			scrollBG();
		});

		// Similar story for a window resize
		$(window).resize(function(){
			scrollBG();
		});
	});

	// Beta Login Info
	function showBetaLogin(){
		document.getElementById('beta-login').style.display = 'block';
		document.getElementById('beta-link').onclick = function(){hideBetaLogin()};
	}

	function hideBetaLogin(){
		document.getElementById('beta-login').style.display = 'none';
		document.getElementById('beta-link').onclick = function(){showBetaLogin()};
	}

	function tryBetaLogin(form){
		//Fine, look at the code and cheat, why don't you. We're just trying to make it less public as we get initial feedback.
		if($('#beta-password').val() == "findoutnow"){
			document.body.style.overflow = 'visible';
			$.scrollTo("#about", 500);
		} else {
			console.log('wrong pass');
		}
		return false;
	}

	// This function moves the backgroud and repositions the splash header to ensure it stays at the top of the page.
	function scrollBG(){
		// vars
		var pos = $(window).scrollTop();
		var height = $("#splash").height();
		var intertia = 0.1;

		// Scroll background
		$("#background").css("background-position", "0px " + String(-pos*intertia) + "px");

		// Repositions the nav.
		$("#nav").css("top", String(Math.max(height, pos) + "px"));

		// ScrollSpy
		// Note: there's probably a cleaner way to do this.
		var posmid = pos + $(window).height()/2;
		if($('#about').offset().top < posmid && posmid < ($('#about').offset().top + $('#about').height())) {
			// console.log('about active!' + ($('#about').offset().top).toString() + ' ' + (posmid).toString() + ' ' + ($('#about').offset().top + $('#about').height()).toString());
			$('#about-link').addClass('nav-link-active');
		} else {
			// console.log('about not active');
			$('#about-link').removeClass('nav-link-active');
		}
		if($('#experience').offset().top < posmid && posmid < ($('#experience').offset().top + $('#experience').height())) {
			// console.log('about active!' + ($('#about').offset().top).toString() + ' ' + (posmid).toString() + ' ' + ($('#about').offset().top + $('#about').height()).toString());
			$('#experience-link').addClass('nav-link-active');
		} else {
			// console.log('about not active');
			$('#experience-link').removeClass('nav-link-active');
		}
		if($('#work').offset().top < posmid && posmid < ($('#work').offset().top + $('#work').height())) {
			// console.log('about active!' + ($('#about').offset().top).toString() + ' ' + (posmid).toString() + ' ' + ($('#about').offset().top + $('#about').height()).toString());
			$('#work-link').addClass('nav-link-active');
		} else {
			// console.log('about not active');
			$('#work-link').removeClass('nav-link-active');
		}
	}

	// Populate the popup with the right content and show it.
	function showPopup(cssId){
		if(cssId!='thanks'){
			var section = $("#"+cssId).closest(".page"); // Ref to the section to which the tile belongs
			if (($(window).scrollTop() - section.offset().top) != 0){ // We scroll to the section first
				$.scrollTo(section, 300);
				$('#popup-background').delay(300).fadeIn(200);
				$('#popup-'+cssId).delay(300).fadeIn(200);
			} else { // No delay
				$('#popup-background').fadeIn(200);
				$('#popup-'+cssId).fadeIn(200);
			}
		}else{
			$('#popup-background').fadeIn(200);
			$('#popup-'+cssId).fadeIn(200);
		}

		$('body').css({'overflow':'hidden'}); // prevents the main body from scrolling

		// Call a redraw for the maps to properly render their size
		setTimeout(function(){
			google.maps.event.trigger(coopMap.map, 'resize');
			google.maps.event.trigger(linkedinMap.map, 'resize');
		}, 300);
	}

	// Hide the popup divs
	function hidePopup(){
		console.log("hide popup called");
		$('#popup-background').fadeOut(200);
		$('.popup').fadeOut(200);
		$('body').css({'overflow':'auto'}); // Allows the page to scroll again
	}
