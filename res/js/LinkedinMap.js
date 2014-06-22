function LinkedinMap(cssId) {
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

LinkedinMap.prototype.generatePoints = function(){

	// TODO offset points

	for(profile in this.mapData){
		if(this.mapData.hasOwnProperty(profile)){

			if(this.mapData[profile]['mapLocation']){

				var jobData = this.mapData[profile];
				var job = new Object();

				job.infoWindowString = "";

				job.infoWindowString += "<div class='info-window'>";
				job.infoWindowString += "<h1>" + jobData['headline'] + "</h1>";
				job.infoWindowString += "<p>" + jobData['industry'] + "</p>";
				job.infoWindowString += "<p><strong>" + jobData['location'] + '</strong></p>';
				job.infoWindowString += "</div>";

				job.marker = new google.maps.Marker({
					position: new google.maps.LatLng(jobData['mapLocation']['lat'],jobData['mapLocation']['lng']),
					map: this.map,
					title: jobData['headline'],
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

LinkedinMap.prototype.resize = function(){
	google.maps.event.trigger(this.map, 'resize');
}

LinkedinMap.prototype.showInfoWindow = function(job, map){
	return function(){
		infoWindow.setContent(job.infoWindowString);
		infoWindow.open(map, job.marker);
	}
}