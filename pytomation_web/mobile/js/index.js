//Global Variables
var serverName;
var userName;
var password;
var deviceData;
var currentTheme;
var auth;
var onServer = false;
var resizeTimer;

var init = function () {
    load_settings();
    if (currentTheme !== 'a') theme_changed(currentTheme);
    get_device_data();
    
    //resize slider, taking the hidden text box into accout
    $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        var device_width = $(window).innerWidth();
        device_width=(device_width / 2) - 38;
        $('.ui-slider-track ').width(device_width);
    }, 200);
});
}; // init
$(document).ready(init);

function theme_changed(selectedTheme){
    $('.ui-body-' + currentTheme).each(function(){
        $(this).removeClass('ui-body-' + currentTheme).addClass('ui-body-' + selectedTheme);    
    });
    $('.ui-btn-up-' + currentTheme).each(function(){
        $(this).removeClass('ui-btn-up-' + currentTheme).addClass('ui-btn-up-' + selectedTheme);    
    });
    $('.ui-btn-down-' + currentTheme).each(function(){
        $(this).removeClass('ui-btn-down-' + currentTheme).addClass('ui-btn-down-' + selectedTheme);    
    });

    $('#main').find('*[data-theme]').each(function(index){
        $(this).attr('data-theme',selectedTheme);
    });
    $('#main').attr('data-theme', selectedTheme).removeClass('ui-body-' + currentTheme).addClass('ui-body-' + selectedTheme).trigger('create');

    $('#settings').find('*[data-theme]').each(function(index){
        $(this).attr('data-theme',selectedTheme);
    });
    $('#settings').attr('data-theme', selectedTheme).removeClass('ui-body-' + currentTheme).addClass('ui-body-' + selectedTheme).trigger('create');

    $('#commands').find('*[data-theme]').each(function(index){
        $(this).attr('data-theme',selectedTheme);
    });
    $('#commands').attr('data-theme', selectedTheme).removeClass('ui-body-' + currentTheme).addClass('ui-body-' + selectedTheme).trigger('create');
    currentTheme = selectedTheme;
} //theme changed

function load_settings() {
    serverName = window.localStorage.getItem("serverName");
    userName = window.localStorage.getItem("userName");
    password = window.localStorage.getItem("password");
    currentTheme = window.localStorage.getItem("currentTheme");

    var settingsForm = document.forms['settingsForm'];
    settingsForm.elements["serverName"].value = serverName;
    settingsForm.elements["userName"].value = userName;
    settingsForm.elements["password"].value = password;
    
    if (currentTheme === null) currentTheme = 'a';
    if (typeof userName === 'undefined' || userName === '') auth=false; else auth = true;
} //Load Settings

function save_settings() {
    var settingsForm = document.forms['settingsForm'];
    serverName = settingsForm.elements["serverName"].value;
    userName = settingsForm.elements["userName"].value;
    password = settingsForm.elements["password"].value;
    window.localStorage.setItem("serverName", serverName);
    window.localStorage.setItem("userName", userName);
    window.localStorage.setItem("password", password);
    window.localStorage.setItem("currentTheme", currentTheme);
    get_device_data();
} //Save Settings

function get_device_data_callback(data) {
    if(data !== null && serverName === '' && onServer === false) {
        //On the server so remove server settings
        $('#serverSettings').css('display','none');
        onServer=true;
    };
    data.sort(function (a,b) {
        if (a['type_name'] === b['type_name']) {
            var x = a['name'].toLowerCase(), y = b['name'].toLowerCase();
            return x < y ? -1 : x > y ? 1 : 0;	
        }
        var x = a['type_name'].toLowerCase(), y = b['type_name'].toLowerCase();
        return x < y ? -1 : x > y ? 1 : 0;
    }); //sort
    deviceData = data;
    reload_device_grid();
}

function get_device_data() {
    if (auth) {
        $.ajax({
            dataType: "json",
            url: serverName + "/api/devices",
            headers: {"Authorization": "Basic " + btoa(userName + ":" + password)},
            crossDomain: true,
            context: document.body,
            type: 'GET',
            error: function(jqXHR, status, errorThrown){
                $("#settingsButton").click();
            } //error
        }).done(get_device_data_callback);
    } else {
        $.ajax({
            dataType: "json",
            url: serverName + "/api/devices",
            crossDomain: true,
            context: document.body,
            type: 'GET',
            error: function(jqXHR, status, errorThrown){
                $("#settingsButton").click();
            } //error
        }).done(get_device_data_callback);
    } // if auth
} // get device data

function reload_device_grid() {
    var devices = [];
    var select = document.getElementsByName('listDevice')[0];
    var deviceColumn = 1;
    var screenSize = $(document).width();
    $.each(deviceData, function(deviceID, values) {
        if (values['type_name'] === select.value) {
            var sliderValue;
            var state = values['state'];
            var deviceID = values['id'];
            var name = values['name'];
            var brAdded=false;
            var buttonLabel="";
            var firstLineLength=0;
            if (name.length > 18) {
                $.each(name.split(' '), function(nameIndex,namepart) {
                    if (namepart.length > 18) namepart = namepart.substring(0,18);
                    if (!brAdded && buttonLabel.length+ namepart.length>17) {
                        buttonLabel += '<br />';
                        brAdded = true;
                        firstLineLength = buttonLabel.length;
                        buttonLabel += namepart;
                    } else
                        buttonLabel += namepart + ' ';
                });
            }
            else
                buttonLabel = name;
            
            if (brAdded) {
                buttonLabel.substring(0,buttonLabel.length + 18 - (buttonLabel.length - firstLineLength + state.length));
                buttonLabel += ' - ' + state;
            }
            else buttonLabel += '<br />' + state;
            
            if (state === 'on')
                sliderValue = 100;
            else if (state === 'off')
                sliderValue = 0;
            else{
                sliderValue = state[1];
            } // slider level
            
            rowData = "";
            if (deviceColumn === 1) {
                rowData+= "<tr class='deviceRow'>";
            }
            rowData += "<td><div data-id='" + values['id'] + "' class='singleDevice'><a href='#commands' style='display: none;'></a>";
            rowData +="<button data-mini='true' data-inline='true' data-role='button' class='toggle' command='toggle' deviceId='" + deviceID + "'>" + buttonLabel + "</button>";
            if (select.value === 'Light') rowData += "<input deviceId='" + deviceID + "' id='slider"  + deviceID + "' value=" + sliderValue + "  data-highlight='true' class='ui-hidden-accessible sliderlevel' type='range' name='points' min='0' max='100'></div></td>";
            else rowData += "</div></td>";
            if (deviceColumn === 2) {
                rowData+= "</tr>";
                deviceColumn = 1;
            }
            else
                deviceColumn = 2;
            
            devices.push(rowData);
        } // if type
    }); // each device
    $("#tableDevices").find("tr").remove();
    $("#tableDevices").append(devices.join('')).trigger('create');
    $(".toggle").click(on_device_command);
    $(".ui-slider").mouseup(send_level);
    $(".ui-slider").touchend(send_level);
    $(".toggle").bind("taphold", commandsPopup);
    
    //resize slider, taking the hidden text box into accout 
    var device_width = $(window).innerWidth();
    device_width=(device_width / 2) - 40;
    $('.ui-slider-track ').width(device_width);
} // reload device grid

function commandsPopup(event) {
    var deviceID = $(this).attr('deviceId');
    update_command_table(deviceID);
    $('div[data-id="' + deviceID + '"] a').click();
} // commandsPopup

function update_command_table(deviceID) {
    $("#tableCommands").find("tr").remove();
    var commands = [];
    $.each(deviceData, function(cacheindex, values) {
        if (values['id'] === deviceID) {
            if (values['commands']) {
                $.each(values['commands'], function(index, command){
                    commands.push("<tr><td><button data-mini='true' data-role='button' class='command' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</button></td></tr>");
                }); //each
                $("#tableCommands").append(commands.join(" ")).trigger('create');
                $(".command").click(on_device_command);
            } // if has commands
        } // if device
    }); //each cached device
} //update command table

function on_device_command(eventObject) {
    command = $(this).attr('command');
    deviceID = $(this).attr('deviceId');
    send_command(deviceID, command);
    return false;
} //on device command

function send_level() {
    var deviceID = $(this).children('input').attr('deviceId');
    send_command(deviceID,'level,' + $(this).children('input').val());
} // send level

function send_command_callback(data) {
    var id = data['id'];
    var state = data['state'];
    var name = data['name'];
    var brAdded=false;
    var buttonLabel="";
    if (name.length > 18) {
        $.each(name.split(' '), function(nameIndex,namepart) {
            if (namepart.length > 18) namepart = namepart.substring(0,18);
            if (!brAdded && buttonLabel.length+ namepart.length>17) {
                buttonLabel += '<br />';
                brAdded = true;
                firstLineLength = buttonLabel.length;
                buttonLabel += namepart;
            } else
                buttonLabel += namepart + ' ';
        });
    }
    else
        buttonLabel = name;

    if (brAdded) {
        buttonLabel.substring(0,buttonLabel.length + 18 - (buttonLabel.length - firstLineLength + state.length));
        buttonLabel += ' - ' + state;
    }
    else buttonLabel += '<br />' + state;
    if (state === 'on')
        sliderValue = 100;
    else if (state === 'off')
        sliderValue = 0;
    else{
        sliderValue = state[1];
    } // slider level
    $('div[data-id="' + id + '"] button.toggle').html(buttonLabel);
    $('#slider' + id).val(sliderValue);
    $('#slider' + id).slider('refresh');
}

function send_command(deviceID, command) {
    if (auth) {
        $.ajax({
            dataType: "json",
            url: serverName + "/api/device/" + deviceID,
            headers: {"Authorization": "Basic " + btoa(userName + ":" + password)},
            crossDomain: true,
            context: document.body,
            type: 'POST',
            data: { command: command },
            error: function(jqXHR, status, errorThrown){
                alert(errorThrown);
            } //error
        }).done(send_command_callback); //done
    } else {
        $.ajax({
            dataType: "json",
            url: serverName + "/api/device/" + deviceID,
            crossDomain: true,
            context: document.body,
            type: 'POST',
            data: { command: command },
            error: function(jqXHR, status, errorThrown){
                alert(errorThrown);
            } //error
        }).done(send_command_callback); //done
    }
} // send command