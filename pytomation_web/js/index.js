//Global Variables
var serverName;
var serverName2;
var currentSever;
var userName;
var password;
var deviceData = {};
var rooms = {};
var currentTheme;
var auth;
var onServer = false;
var resizeTimer;
var ws;
var wsAttempts = 0;
var wsRetrying = false;
var upgradeConnection;
var style = "compact";
var changingStyle = false;
var isCordovaApp= !!window.cordova;
var isMobile;

//document.addEventListener("deviceready", init, false);

function init() {
    //Prevents sending toggle command when opening command popup
    $.event.special.tap.emitTapOnTaphold = false;
    
    //set isMobile
    if (isCordovaApp)
        isMobile = true;
    else
        (function(a){isMobile=/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))})(navigator.userAgent||navigator.vendor||window.opera);
    window.isAndroid = navigator.userAgent.indexOf('Android') !== -1;
    //fix for Dolphin not being detected as mobile
    if (window.isAndroid) isMobile = true;
    
    $('.colorSelect').click(theme_changed);
    
    load_settings();
    if (currentTheme !== 'a') theme_changed(currentTheme);
    
    //resize sliders, taking the hidden text box into accout
    $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(recalc_device_content_size, 200);
    }); //resizeTimer
    
    // Voice Command pulldown
    if((window.isAndroid && isCordovaApp) || (window.chrome && !isMobile)) {
        $(".iscroll-wrapper", $('#main')).bind( {
            iscroll_onpulldown : doVoice
        } );
    }
    else {
        $(".iscroll-wrapper").data("mobileIscrollview").destroy();
        $(".iscroll-pulldown").remove();
    } // Voice Command pulldown
    get_device_data_ajax();
}; // init
$(document).ready(init);

function theme_changed(selectedTheme){
    // If called from html element get element theme value
    if(typeof selectedTheme === "object") selectedTheme = this.getAttribute('data-pytoTheme');
    $('.ui-overlay-' + currentTheme).each(function(){
        $(this).removeClass('ui-overlay-' + currentTheme).addClass('ui-overlay-' + selectedTheme);    
    });
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
    $('#main').attr('data-theme', selectedTheme).removeClass('ui-page-theme-' + currentTheme).addClass('ui-page-theme-' + selectedTheme).trigger('create');

    $('#settings').find('*[data-theme]').each(function(index){
        $(this).attr('data-theme',selectedTheme);
    });
    $('#settings').attr('data-theme', selectedTheme).removeClass('ui-page-theme-' + currentTheme).addClass('ui-page-theme-' + selectedTheme).trigger('create');

    $('#commands').find('*[data-theme]').each(function(index){
        $(this).attr('data-theme',selectedTheme);
    });
    $('#commands').attr('data-theme', selectedTheme).removeClass('ui-page-theme-' + currentTheme).addClass('ui-page-theme-' + selectedTheme).trigger('create');
    if (selectedTheme > 'e') 
        $('.iscroll-pulldown').css('background','#F9F9F9');
    else
        $('.iscroll-pulldown').css('background','#FFFFFF');
    currentTheme = selectedTheme;
} //theme changed

function get_storage_item(key) {
    item = window.localStorage.getItem(key);
    if (item==='null' || item === null) return ''; 
    else return item;
}

function load_settings() {
    serverName = get_storage_item("serverName");
    serverName2 = get_storage_item("serverName2");
    userName = get_storage_item("userName");
    password = get_storage_item("password");
    currentTheme = get_storage_item("currentTheme");
    style = get_storage_item("style");
    currentServer = serverName;
    if (style === '')
        if (isMobile) style = 'compact' ;
        else style = 'detail';
    var settingsForm = document.forms['settingsForm'];
    settingsForm.elements["serverName"].value = serverName;
    settingsForm.elements["serverName2"].value = serverName2;
    settingsForm.elements["userName"].value = userName;
    settingsForm.elements["password"].value = password;
    settingsForm.elements["LayoutStyle"].value = style;
    if (currentTheme === '') currentTheme = 'a';
    auth = (userName!=='');
} //Load Settings

function save_settings() {
    var settingsForm = document.forms['settingsForm'];
    serverName = settingsForm.elements["serverName"].value;
    serverName2 = settingsForm.elements["serverName2"].value;
    userName = settingsForm.elements["userName"].value;
    password = settingsForm.elements["password"].value;
    style = settingsForm.elements["LayoutStyle"].value;
    window.localStorage.setItem("serverName", serverName);
    window.localStorage.setItem("serverName2", serverName2);
    window.localStorage.setItem("userName", userName);
    window.localStorage.setItem("password", password);
    window.localStorage.setItem("currentTheme", currentTheme);
    window.localStorage.setItem("style", style);
    currentServer = serverName;
    auth = (userName!=='');
    get_device_data_ajax();
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
    var availableTypes = {};
    var optionList = "<option selected value='All'>All Rooms</option>";
    $.each(data, function(index, values) {
        if (values['commands'] !== null ) {
            currentID = values['id'];
            deviceData[currentID] = values;
            if (values['type_name'] === 'Room'){
                optionList += "<option value='" + values['id'] + "'>" + values['name'] + "</option>";
                rooms[currentID] = values['devices'];
            }
            if (!availableTypes.hasOwnProperty(values['type_name'])) availableTypes[values['type_name']] = true;
        }
    });
    //Attach real device data to rooms dictionary
    //Done after to ensure all device data exists
    $.each(rooms, function(roomID, values) {
        var roomList = {};
        $.each(values, function(index, deviceID) {
            roomList[deviceID] = deviceData[deviceID];
        });
        rooms[roomID] = roomList;
    });
    var element = $("#listRoom").html(optionList);
    //jQuery mobile error work-around, seemingly a race condition
    var stillTrying = true;
    while (stillTrying){
        try{
            element.selectmenu().selectmenu("refresh");
            stillTrying = false;
        }
        catch(err){

        }
    }
    
    optionList = "<option selected value='All'>All</option>";
    $.each(availableTypes, function(type_name, value) {
        optionList += "<option value='" + type_name + "'>" + type_name + "</option>";
    });
    element = $("#listDevice").html(optionList);
        
    //jQuery mobile error work-around, seemingly a race condition
    stillTrying = true;
    while (stillTrying){
        try{
            element.selectmenu().selectmenu("refresh");
            stillTrying = false;
        }
        catch(err){

        }
    }
    reload_device_grid();
    setup_ws_connection();
    $(".iscroll-wrapper").data("mobileIscrollview").refresh();
}

function setup_ws_connection() {
    try {
        wsAttempts += 1;
        if (ws){
            try {
                ws.close();
            }
            catch (e) {fake = true;} 
        }
        if (onServer) {
            var loc = window.location, new_url, path;
            if (loc.protocol === "https:") {
                new_url = "wss:";
            } else {
                new_url = "ws:";
            }
            new_url += "//" + loc.host + "/api/bridge";
            ws = new WebSocket(new_url);
        } else {
            if(currentServer.substring(0,5) === 'https'){
                protocol = 'wss://';
                websocketserver = currentServer.substring(8, serverName.length);
            } else {
                protocol = 'ws://';
                websocketserver = currentServer.substring(7, serverName.length);
            }

            if (auth) {
                ws = new WebSocket(protocol + userName + ':' + password + '@' + websocketserver + "/api/bridge");
            } else {
                ws = new WebSocket(protocol + websocketserver + "/api/bridge");
            }
        }
        ws.onmessage = function(e) {
            data = e.data;
            data = $.parseJSON(data);
            if (data !== 'success') { //just an ack from command
                if(typeof data.previous_state === "undefined"){
                    //this isn't a device state update, so it's a device list update
                    get_device_data_callback(data);
                }
                else{ //must be a device state update
                    update_device_state(data);
                }
            }
        };
        ws.onerror = function(e) {
            upgradeConnection = false;
            wsRetrying = true;
            if (wsAttempts === 0) setup_ws_connection();
            else if (wsAttempts < 20) setTimeout(setup_ws_connection,3000);
            else if (wsAttempts < 60) setTimeout(setup_ws_connection,10000);
            else setTimeout(setup_ws_connection,60000);
        };
        ws.onopen = function(e) {
            upgradeConnection = true;
            wsAttempts = 0;
            if (wsRetrying) {
                wsRetrying = false;
                ws.send(JSON.stringify({
                    path: "devices"
                }));
            }
        };
    }
    catch(e){
        //can't do web sockets
        upgradeConnection = false;
    }
}

function check_ws_connection(){
    if (ws.readyState === 1) {
        return true;
    }
    else {
        setup_ws_connection();
    }
}

function recalc_slider_size() {
    var device_width = $(window).innerWidth();
    device_width=(device_width / 2) - 40;
    $('.ui-slider-track ').width(device_width);
}

function recalc_device_content_size(){
    recalc_slider_size();
    
    $("#tableDevices > tbody > tr").each(function(i, row) {
        var LeftDevice = $(row.children[0].children[0]);
        var RightDevice = $(row.children[1].children[0]);
        var LeftDeviceContentHeight = $(row.children[0].children[0].children[0]).height();
        var RightDeviceContentHeight = $(row.children[1].children[0].children[0]).height();
        var ContentHeight;
        if (LeftDeviceContentHeight > RightDeviceContentHeight) 
            ContentHeight = LeftDeviceContentHeight;
        else
            ContentHeight = RightDeviceContentHeight;
        
        LeftDevice.height(ContentHeight);
        RightDevice.height(ContentHeight);
    });
    
    $(".iscroll-wrapper").data("mobileIscrollview").refresh();
}

function get_device_data_ajax() {
    var url;
    if (currentServer === '') {
        url = "/api/devices";
    } else {
        url = currentServer + "/api/devices";
    };
    
    if (auth) {
        $.ajax({
            dataType: "json",
            url: url,
            headers: {"Authorization": "Basic " + btoa(userName + ":" + password)},
            crossDomain: true,
            context: document.body,
            type: 'GET',
            error: function(jqXHR, status, errorThrown){
                if (currentServer !== serverName2) {
                    currentServer = serverName2;
                    get_device_data_ajax();
                } else {
                    $("#settingsButton").click();
                }
            } //error
        }).done(get_device_data_callback);
    } else {
        $.ajax({
            dataType: "json",
            url: url,
            crossDomain: true,
            context: document.body,
            type: 'GET',
            error: function(jqXHR, status, errorThrown){
                if (currentServer !== serverName2) {
                    currentServer = serverName2;
                    get_device_data_ajax();
                } else {
                    $("#settingsButton").click();
                }
            } //error
        }).done(get_device_data_callback);
    } // if auth
} // get device data

function reload_device_grid() {
    var devices = [];
    var devicesLong = [];
    var select = document.getElementsByName('listDevice')[0];
    var room = document.getElementsByName('listRoom')[0];
    var deviceColumn = 1;
    var screenSize = $(document).width();
    var deviceList;
    
    if (room.value === 'All') 
        deviceList = deviceData;
    else {
        deviceList = rooms[room.value];
        var values = deviceData[room.value];
        var buttonLabel = values['state'];
        if (buttonLabel !== 'unknown') {
            var rowData = "<tr class='deviceRow'><td><div data-id='" + values['id'] + "' class='singleDevice'>";
            rowData += "<button data-mini='true' data-role='button' class='room_toggle' command='toggle' deviceId='" + room.value + "'>" + buttonLabel + "</button>";
            rowData += "</div></td><tr>";
            devicesLong.push(rowData);
        }
    }
    $.each(deviceList, function(deviceID, values) {
        if (select.value === 'All' || values['type_name'] === select.value) {
            var sliderValue;
            var state = values['state'];
            var name = values['name'];
            var brAdded=false;
            var buttonLabel="";
            var firstLineLength=0;
            var setpoint = 0;
            var mode = 'off';
            var temp = 0;
            var tempTransitionLabel = 'to';
            if (values['type_name'] === 'Thermostat') {
                $.each(state, function(stateIndex, statePart) {
                    if (statePart[0] === 'temp') temp = statePart[1] + '°';
                    if (statePart[0] === 'mode') mode = statePart[1];
                    if (statePart[0] === 'setpoint') {setpoint = statePart[1]; buttonLabel=setpoint + '°';}
                }); //each
            } else {
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
                else if (state === 'off'){
                    sliderValue = 0;
                    tempTransitionLabel = '';
                }
                else {
                    sliderValue = state[1];
                } // slider level
            }
            
            rowData = "";
            if (deviceColumn === 1) {
                rowData+= "<tr class='deviceRow'>";
            }
            else if (values['type_name'] === 'Thermostat') {
                rowData+= "</tr><tr class='deviceRow'>";
            }
            rowData += "<td><div class=leftDeviceContent><div data-id='" + values['id'] + "' class='singleDevice'><a href='#commands' class='commandPopupToggle' style='display: none;'></a>";
            
            if (values['type_name'] === 'Thermostat'){
                rowData += "<table style='width:100%'><tr><td class='temperature' style='width:2em;padding-left:.5em'>" + temp;
                rowData += "</td><td><select deviceId='" + deviceID + "' class='thermostatMode' data-mini='true' name='listDevice'>";
                $.each(values['commands'], function(index, command){
                    if (command === 'cool')
                        if (mode === command)
                            rowData += "<option selected value='cool'>cooling</option>";
                        else
                            rowData += "<option value='cool'>cooling</option>";
                    else if (command === 'heat')
                        if (mode === command)
                            rowData += "<option selected value='heat'>heating</option>";
                        else
                            rowData += "<option value='heat'>heating</option>";
                    else if (command === 'off')
                        if (mode === command)
                            rowData += "<option selected value='off'>off</option>";
                        else
                            rowData += "<option value='off'>off</option>";
                    else if (command === 'automatic')
                        if (mode === command)
                            rowData += "<option selected value='automatic'>automatic</option>";
                        else
                            rowData += "<option value='automatic'>automatic</option>";
                }); //each
                rowData += '</select></td><td style="width:1em;padding-left:.5em">' + tempTransitionLabel + '</td><td style="width:2em"><a href="#" deviceId="' + deviceID + '" class="decrementSetpoint" data-iconpos="notext" data-role="button" data-icon="minus"></a></div></td>';
                rowData += '<td style="width:3em"><button data-mini="true" data-role="button" class="thermSetpoint" deviceId="' + deviceID + '">' + buttonLabel + "</button></td>";
                rowData += '<td style="width:2em"><a href="#" deviceId="' + deviceID + '" class="incrementSetpoint" data-iconpos="notext" data-role="button" data-icon="plus"></a></div></td></tr></table></tr>';
            } else {
                rowData += "<button data-mini='true' data-role='button' class='toggle' command='toggle' deviceId='" + deviceID + "'>" + buttonLabel + "</button>";
                if (values['type_name'] === 'Light') 
                    rowData += "<input deviceId='" + deviceID + "' id='slider"  + deviceID + "' value=" + sliderValue + "  data-highlight='true' class='ui-hidden-accessible sliderlevel' type='range' name='points' min='0' max='100'></div></td>";
                else
                    rowData += "</div></div></td>";
            }
            
            if (values['type_name'] === 'Thermostat'){
                devicesLong.push(rowData);
            } else {
                if (style === "compact") {
                    if (deviceColumn === 2) {
                        rowData+= "</tr>";
                        deviceColumn = 1;
                    }
                    else
                        deviceColumn = 2;
                } else
                    rowData+= "<td><div class='singleDevice2'><div class=commandContent>" + build_command_list(values['id'],"mini") + "</div></div></td></tr>";
                devices.push(rowData);
            }
        } // if type
    }); // each device
    if (deviceColumn === 2 ) {
        devices.push("<td><div class='singleDevice2' style='border-style: none;'></td></tr>");
    }
    if (devices) {
        $("#tableDevices").find("tr").remove();
        $("#tableDevices").append(devices.join('')).trigger('create');
    }
    if (devicesLong) {
        $("#tableDevicesLong").find("tr").remove();
        $("#tableDevicesLong").append(devicesLong.join('')).trigger('create');
    }

    //Add and event handlers
    $(".toggle").click(on_device_command);
    $(".room_toggle").click(on_device_command);
    $(".decrementSetpoint").click(decrementSetpoint);
    $(".incrementSetpoint").click(incrementSetpoint);
    $(".ui-slider").mouseup(send_level);
    $(".ui-slider").touchend(send_level);
    $('.thermostatMode').bind("change", changeMode);
    if (style === "compact" && isMobile){
        $(".toggle").bind("taphold", commandsPopup);}
    else
        $(".toggle").contextmenu(function(e) {
            e.preventDefault();
            if(e.which === 3) {
                var deviceID = $(this).attr('deviceId');
                commandsPopup(deviceID);
            }
        });
    if (style !== "compact") $(".command").click(on_device_command);
    
    //resize slider, taking the hidden text box into accout 
    recalc_slider_size();
    
    //recalculate slider size when scrollbars appear (only in desktop version)
    setTimeout(recalc_device_content_size,500);
} // reload device grid

function update_device_state(data) {
    if (data === 'success') return;
    var id = data['id'];
    var state = data['state'];
    var name = data['name'];
    var brAdded=false;
    var buttonLabel="";
    var setpoint = 0;
    var mode = 'off';
    var temp = 0;
    deviceData[id]['state'] = state;
    if (data['type_name'] === 'Thermostat') {
        $.each(state, function(stateIndex, statePart) {
            if (statePart[0] === 'temp') temp = statePart[1] + '°';
            if (statePart[0] === 'mode') mode = statePart[1];
            if (statePart[0] === 'setpoint') {setpoint = statePart[1]; buttonLabel=setpoint + '°';}
        }); //each
        $('div[data-id="' + id + '"] .temperature').html(temp);
        $('div[data-id="' + id + '"] button.toggle').html(buttonLabel);
        var element = $('div[data-id="' + id + '"] .thermostatMode ');
        element.val(mode);

        //jQuery mobile error work-around, seemingly a race condition
        var stillTrying = true;
        while (stillTrying){
            try{
                element.selectmenu().selectmenu("refresh");
                stillTrying = false;
            }
            catch(err){

            }
        }
            
    } else {
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
        if (data['type_name'] === 'Room') {
            buttonLabel = data['state'];
            if (buttonLabel === 'unknown') buttonLabel = "Occupancy Unknown";
            $('div[data-id="' + id + '"] button.room_toggle').html(buttonLabel);
        }
        $('#slider' + id).val(sliderValue);
        $('#slider' + id).slider('refresh');
    } // if type name
}

function send_command(deviceID, command) {
    if (upgradeConnection) {
        check_ws_connection();
        ws.send(JSON.stringify({
            path: "device/" + deviceID,
            command: command
        }));
    } else {
        send_command_ajax(deviceID, command);
    }
}

function send_command_ajax(deviceID, command) {
    var url;
    if (currentServer === '') {
        url = "/api/device/" + deviceID;
    } else {
        url = currentServer + "/api/device/" + deviceID;
    };
    if (auth) {
        $.ajax({
            dataType: "json",
            url: url,
            headers: {"Authorization": "Basic " + btoa(userName + ":" + password)},
            crossDomain: true,
            context: document.body,
            type: 'POST',
            data: { command: command },
            error: function(jqXHR, status, errorThrown){
                alert(status + errorThrown);
            } //error
        }).done(update_device_state); //done
    } else {
        $.ajax({
            dataType: "json",
            url: url,
            crossDomain: true,
            context: document.body,
            type: 'POST',
            data: { command: command },
            error: function(jqXHR, status, errorThrown){
                alert(status + errorThrown);
            } //error
        }).done(update_device_state); //done
    }
} // send command

function doVoice(event, data) {
    var maxMatches = 3;
    if (window.chrome) {
        var recognizer = new webkitSpeechRecognition();
        recognizer.onresult = function(event) {
            //var command = [event.results[0][0].transcript];
            send_voice_command([event.results[0][0].transcript]);
            data.iscrollview.refresh();
        };
        recognizer.onerror = function(event) {
            alert(event.message);
            data.iscrollview.refresh();
        };
        recognizer.start();
    } else {
        window.plugins.speechrecognizer.startRecognize(function(result){
            send_voice_command(result);
            data.iscrollview.refresh();
        }, function(errorMessage){
            alert("Error message: " + errorMessage);
            data.iscrollview.refresh();
        }, maxMatches, 'Speak now');
    }
};

function send_voice_command(command) {
    if (upgradeConnection) {
        check_ws_connection();
        ws.send(JSON.stringify({
            path: "voice",
            command: command
        }));
    } else {
        send_voice_command_ajax(command);
    }
}

function send_voice_command_ajax(command) {
    var url;
    if (currentServer === '') {
        url = "/api/voice";
    } else {
        url = currentServer + "/api/voice";
    };
    if (auth) {
        $.ajax({
            dataType: "json",
            url: url,
            headers: {"Authorization": "Basic " + btoa(userName + ":" + password)},
            crossDomain: true,
            context: document.body,
            type: 'POST',
            data: { command: command },
            error: function(jqXHR, status, errorThrown){
                alert(status + errorThrown);
            } //error
        }).done(update_device_state); //done
    } else {
        $.ajax({
            dataType: "json",
            url: url,
            crossDomain: true,
            context: document.body,
            type: 'POST',
            data: { command: command },
            error: function(jqXHR, status, errorThrown){
                alert(status + errorThrown);
            } //error
        }).done(update_device_state); //done
    }
} // send voice command

function send_level() {
    var deviceID = $(this).children('input').attr('deviceId');
    send_command(deviceID,'level,' + $(this).children('input').val());
    $(this).click();
    jQuery(document).trigger('mouseup');
} // send level

function changeMode(eventObject){
    deviceID = $(this).attr('deviceId');
    command = $(this).val();
    send_command(deviceID, command);
}

function decrementSetpoint(eventObject){
    deviceID = $(this).attr('deviceId');
    var setpoint = 0;
    $.each(deviceData[deviceID]['state'], function(stateIndex, statePart) {
        if (statePart[0] === 'setpoint') {setpoint = --statePart[1];}
    }); //each
    send_command(deviceID,'setpoint,' + setpoint);
}

function incrementSetpoint(eventObject){
    deviceID = $(this).attr('deviceId');
    var setpoint = 0;
    $.each(deviceData[deviceID]['state'], function(stateIndex, statePart) {
        if (statePart[0] === 'setpoint') {setpoint = ++statePart[1];}
    }); //each
    send_command(deviceID,'setpoint,' + setpoint);
}

function commandsPopup(deviceID) {
    var myDeviceID;
     if (typeof deviceID !== 'object')
        myDeviceID = deviceID;
    else 
        myDeviceID = $(this).attr('deviceId');
    $("#tableCommands").find("tr").remove();
    $("#tableCommands").append(build_command_list(myDeviceID, "full")).trigger('create');
    $(".command").click(on_device_command);
    $('div[data-id="' + myDeviceID + '"] a.commandPopupToggle').click();
} // commandsPopup

function build_command_list(deviceID, mode) {
    var commands = [];
    $.each(deviceData, function(cacheindex, values) {
        if (values['id'] === deviceID) {
            if (values['commands']) {
                $.each(values['commands'], function(index, command){
                    if (mode === "full") {
                        commands.push("<tr><td><button data-mini='true' data-role='button' class='command' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</button></td></tr>");
                    } else {
                        commands.push("<a data-inline='true' data-mini='true' data-role='button' class='command' command='" + command + "' deviceId='" + values['id'] + "'>" + command + "</a>");
                    }
                }); //each
            } // if has commands
        } // if device
    }); //each cached device
    return commands.join(" ");
} //update command table

function on_device_command(eventObject) {
    command = $(this).attr('command');
    deviceID = $(this).attr('deviceId');
    send_command(deviceID, command);
    return false;
} //on device command