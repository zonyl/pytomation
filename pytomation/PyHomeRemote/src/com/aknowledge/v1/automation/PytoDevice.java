/**
    This file is part of PyHomeRemote

    PyHomeRemote is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyHomeRemote is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyHomeRemote.  If not, see <http://www.gnu.org/licenses/>. * 

	Written by Anand Kameswaran
 */
package com.aknowledge.v1.automation;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.os.Parcel;
import android.os.Parcelable;
import android.util.Log;

public class PytoDevice implements Parcelable{
	String devID;
	String[] devCommands;
	String devType;
	String devState;
	String devName;
	
	public String getDevID() {
		return devID;
	}

	public void setDevID(String devID) {
		this.devID = devID;
	}

	public String getDevType() {
		return devType;
	}

	public void setDevType(String devType) {
		this.devType = devType;
	}

	public String getDevState() {
		return devState;
	}

	public void setDevState(String devState) {
		this.devState = devState;
	}

	public String getDevName() {
		return devName;
	}

	public void setDevName(String devName) {
		this.devName = devName;
	}


	public PytoDevice()
	{

	}
	
	public PytoDevice(JSONObject json){
		try {
			this.devID = json.getString("id");
			
			this.devType = json.getString("type_name");
			Log.d("PytoDevice", this.devID + " is of type " + this.devType);
			if (!devType.equalsIgnoreCase("UPB")) {
				JSONArray jsa = json.getJSONArray("commands");
				devCommands = new String[jsa.length()];
				for (int i = 0; i < jsa.length(); i++) {
					devCommands[i] = (String) jsa.get(i);
				}
			}else
			{
				devCommands = new String[]{"NONE"};
			}
			this.devState = json.getString("state");
			this.devName = json.getString("name");
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		
	}

	@Override
	public int describeContents() {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public void writeToParcel(Parcel dest, int flags) {
		dest.writeString(devID);
		dest.writeStringArray(devCommands);
		dest.writeString(devName);
		dest.writeString(devState);
		dest.writeString(devType);
		
	}
	@Override
	public String toString(){
		String retval = this.devID + " NAME: " 
					+this.devName +" : STATE: " 
					+ this.devState +" TYPE: " 
					+ this.devType + " COMMANDS: " 
					+ this.devCommands.toString();
		return retval;
	}

 public PytoDevice createFromParcel(Parcel source) { 
     PytoDevice mDevice = new PytoDevice(); 
     mDevice.devID = source.readString(); 
     mDevice.devCommands = source.createStringArray();
     mDevice.devName = source.readString();
     mDevice.devState = source.readString();
     mDevice.devType = source.readString();
     return mDevice; 
 }  

}
