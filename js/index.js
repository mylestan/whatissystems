$('#nav a').click(function (e) {
  e.preventDefault();
  $(this).tab('show');
})
$('#home a:[href="#homeTab"]').tab('show')
$('#about a:last').tab('show')