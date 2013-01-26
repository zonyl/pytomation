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
				rowData = "<tr id='" + deviceID + "'><td>" + values['name'] + "</td><td>" + values['state'] + "</td>";
				rowData += "<td>";
				commands = [];
				if (values['commands']) {
					$.each(values['commands'], function(index, command){
						commands.push("<a href='' class='command' command='" + command + "' deviceId='" + deviceID + "'>" + command + "</a>");
					});
				}
				rowData += commands.join(" ") + "</td></tr>";
				devices.push(rowData);
			});
		$("#tableDevices").append(devices.join(''));
		$(".command").click(on_device_command);
	});
}

function on_device_command(eventObject)
{
	command = $(this).attr('command');
	deviceID = $(this).attr('deviceId');
	$.ajax({
	  dataType: "json",
//	  url: "/api/device/" + deviceID + "/" + command,
	  url: "/api/device/" + deviceID,
	  context: document.body,
	  type: 'POST',
	  data: { command: command },
	}).done(function( data ) {
		var a = data;		
	});
	//return false;
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
