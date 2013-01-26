function reload_device_grid()
{
	var devices = []
	$.ajax({
	  dataType: "json",
	  url: "/api/devices",
	  context: document.body,
	  type: 'GET',
	}).done(function( data ) {
		var devices = [];
		$.each(data, function(deviceID, values) {
				rowData = "<tr><td id='" + deviceID + "'>" + values['name'] + "</td><td>" + values['state'] + "</td>";
				rowData += "<td>";
				commands = [];
				if (values['commands']) {
					$.each(values['commands'], function(index, command){
						commands.push("<a href='' command='" + command + "' deviceId='" + deviceID + "'>" + command + "</a>");
					});
				}
				rowData += commands.join(" ") + "</td></tr>";
				devices.push(rowData);
			});
		$("#tableDevices").append(devices.join(''));
	});
}

function on_device_command(id, command)
{

}


/*
$.getJSON('api/devices', function(data) {
  var items = [];
 
  $.each(data, function(key, val) {
    items.push('<li id="' + key + '">' + val + '</li>');
  });
  
  $('<ul/>', {
    'class': 'my-new-list',
    html: items.join('')
  }).appendTo('body');
});
*/
