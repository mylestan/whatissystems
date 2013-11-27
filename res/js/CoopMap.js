function CoopMap(cssId) {
	// Properties
	this.mapData = new Object(); // Access to the raw data
	this.cssId = cssId; // the CSS id of the map
	this.mapOptions = {
	    zoom: 2,
	    center: new google.maps.LatLng(43.4722,-80.5472),
	    mapTypeId: google.maps.MapTypeId.MAP
	};

	this.map = new google.maps.Map(document.getElementById(this.cssId), this.mapOptions); // The map
	this.infoWindow = new google.maps.InfoWindow(); // The info window on the map
	this.jobs = new Array(); // of all the points
}

CoopMap.prototype.generatePoints = function(){

	// TODO offset points

	for(profile in this.mapData){
		if(this.mapData.hasOwnProperty(profile)){

			var locationArray = new Array();

			for(term in this.mapData[profile]){
				if(this.mapData[profile].hasOwnProperty(term)){
					if(this.mapData[profile][term].hasOwnProperty('mapLocation')){ //In theory, the list should not contain profiles which do not have a mapLocation.

						var jobData = this.mapData[profile][term]; // For reference

						// Make an object for each marker
						var job = new Object();
						job.infoWindowString = "";

						job.infoWindowString += "<div class='info-window'>";
						job.infoWindowString += "<h1>" + jobData['title'] + " at " + jobData['employer'] + "</h1>"; // TODO add URL for site
						job.infoWindowString += "<p>" + ordinate(jobData['termNumber']) + " co-op term, " + jobData['term'] + ' ' + jobData['year'] + '</p>'; // TODO ordinal number ending
						job.infoWindowString += "<p><strong>" + jobData['city'] + ', ' + jobData['province'] + ', ' + jobData['country'] + '</strong></p>';
						job.infoWindowString += "</div>";

						// Add the marker
						job.marker = new google.maps.Marker({
							position: new google.maps.LatLng(jobData['mapLocation']['lat'],jobData['mapLocation']['lng']),
							map: this.map,
							title: jobData['title'] + ', ' + jobData['company'],
							animation: google.maps.Animation.DROP
		  				});
		  				job.marker.setVisible(true);

		  				// Add listener
		  				google.maps.event.addListener(job.marker, 'click', this.showInfoWindow(job, this.map));

		  				// Push to array
		  				this.jobs.push(job);
					}
				}
			}
		}
	}
}

CoopMap.prototype.resize = function(){
	google.maps.event.trigger(this.map, 'resize');
}

CoopMap.prototype.showInfoWindow = function(job, map){
	return function(){
		infoWindow.setContent(job.infoWindowString);
		infoWindow.open(map, job.marker);
	}
}