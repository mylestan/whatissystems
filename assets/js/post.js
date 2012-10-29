function createThumbnails(imgSrc, i){
	//variables
	var thumb = new Image();
	var thumbPath = imgSrc + '/' + i + '-thumb.jpg';

	//image values
	thumb.src = thumbPath;
	thumb.id = i;

	//making the new div
	var thumbDiv = document.createElement('div');

	//assigns one first thumbnail to be active, corresponting to '1-img.jpg' being displayed by default in post.html
	if (i === 1){
		thumbDiv.setAttribute('class', 'thumb-active');
	}
	else{
		thumbDiv.setAttribute('class', 'thumb');
	}

	//add image to the div
	$(thumbDiv).append(thumb);
	$("#thumbnails").append(thumbDiv);

	//if it loaded correctly, call for next thumbnail
	$("#" + thumb.id).load( function() {
		createThumbnails(imgSrc, i + 1);
	});

	//if error is thrown (aka doesn't exist), remove element
	$("#" + thumb.id).error (function() {
		$("#" + thumb.id).remove();
	});
}
