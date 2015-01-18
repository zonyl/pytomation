function clear_device_grid()
{
	$("#tableDevices").find("tr").remove();
}

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
		data.sort(function (a,b)
		{
		   if (a['type_name'] == b['type_name'])
		   {
		        var x = a['name'].toLowerCase(), y = b['name'].toLowerCase();
		        return x < y ? -1 : x > y ? 1 : 0;		   		
		   }
		   var x = a['type_name'].toLowerCase(), y = b['type_name'].toLowerCase();
	        return x < y ? -1 : x > y ? 1 : 0;		   		
		   
		});
		
		var select = document.getElementsByName('listDevice')[0];
	    	    
		var last_type = null;
		$.each(data, function(deviceID, values) {
				if ( select.value == 'all' ) {
					rowData = "";
					if (values['type_name'] != last_type){
						rowData += "<tr><Td colspan=3>" + values['type_name'] + "<td></tr>";
						last_type = values['type_name'];
					}
					rowData += "<tr data-id='" + values['id'] + "'><td></td>";
					rowData += "<td>" + values['name'] + "</td>";
					rowData += "<td class='state'>" + values['state'] + "</td>";
					rowData += "<td class='commands'>";
					commands = [];
					if (values['commands']) {
						$.each(values['commands'], function(index, command){
							if ('junk' == values['state']) {
								commands.push("<button class='command btn btn-sm' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</button>");
							} else {
								commands.push("<button class='command btn btn-primary btn-sm' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</button>");
							}
						});
					}
					rowData += commands.join(" ") + "</td></tr>";
					devices.push(rowData);
				
				} else if (values['type_name'] == select.value) {
					
					rowData = "";
					if (values['type_name'] != last_type){
						rowData += "<tr><Td colspan=3>" + values['type_name'] + "<td></tr>";
						last_type = values['type_name'];
					}
					rowData += "<tr data-id='" + values['id'] + "'><td></td>";
					rowData += "<td>" + values['name'] + "</td>";
					rowData += "<td class='state'>" + values['state'] + "</td>";
					rowData += "<td class='commands'>";
					commands = [];
					if (values['commands']) {
						$.each(values['commands'], function(index, command){
							if ('junk' == values['state']) {
								commands.push("<button class='command btn btn-small' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</button>");
							} else {
								commands.push("<button class='command btn btn-primary btn-small' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</button>");
							}
						});
					}
					rowData += commands.join(" ") + "</td></tr>";
					devices.push(rowData);
				}
			});
		clear_device_grid();
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
		var id = data['id'];
		var state = data['state'];
		$('tr[data-id="' + id + '"] td.state').text(state);
	});
	return false;
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
