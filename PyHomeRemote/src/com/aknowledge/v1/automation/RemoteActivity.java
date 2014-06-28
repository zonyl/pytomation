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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.android.volley.AuthFailureError;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request.Method;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;

import android.app.Activity;
import android.app.ActionBar;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.os.Bundle;
import android.os.Handler;
import android.preference.PreferenceManager;
import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.view.View.OnClickListener;
import android.widget.ArrayAdapter;
import android.widget.GridView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.RemoteViewsService.RemoteViewsFactory;

public class RemoteActivity extends Activity implements
		ActionBar.OnNavigationListener,
		RemotePanelFragment.onButtonClickListener {

	private static final String STATE_SELECTED_NAVIGATION_ITEM = "selected_navigation_item";
	// don't want to check objects and preferences too often.
	protected PyHomeController myApp;

	// abstraction layer so I have even less clue what thread things run in

	// UI fragment
	RemotePanelFragment remoteFrag;

	// opiate for the impatient
	ProgressDialog dialog;

	// this should probably be some better container in the future - works for
	// now.
	ArrayList<PytoDevice> myDevices = null;

	String hostname;
	String user;
	String pass;
	int refreshRate = 15000;
	String statusTag = "STATUS";
	String commandTag = "COMMAND";
	Handler handler;

	public void onDevicesLoaded(String result) {
		Log.d("RemoteActivity", "devices loaded: " + result);

		if (dialog != null && dialog.isShowing()) {
			dialog.dismiss();
		}
		if (result != null) {
			parseMyDevices(result);
			createRemotePanel();
		} else {
			AlertDialog alertDialog = new AlertDialog.Builder(this).create();
			alertDialog.setTitle("Problems with your server info.");
			alertDialog
					.setMessage("You should check your settings and try again.");
			alertDialog.setButton("OK", new DialogInterface.OnClickListener() {
				public void onClick(DialogInterface dialog, int which) {
					
				}
			});
			// Set the Icon for the Dialog
			alertDialog.show();

		}

	}

	public void onCommandExecuted(String viewTag, String result) {

		if (result != null) {
			for (PytoDevice dev : myDevices) {
				View myView = remoteFrag.getView().findViewWithTag(viewTag);
				if (dev.getDevID().equalsIgnoreCase(viewTag)) {
					try {
						JSONObject jso = new JSONObject(result);
						String devState = jso.getString("state");
						dev.setDevState(devState);
						if (devState.equalsIgnoreCase("on")) {
							myView.setBackgroundResource(R.drawable.light_bulb_on);
						} else {
							if (devState.equalsIgnoreCase("off")) {
								myView.setBackgroundResource(R.drawable.light_bulb_off);
							} else {
								myView.setBackgroundResource(R.drawable.light_bulb_dimmed);
							}
						}

					} catch (JSONException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
			}
		}
	}

	public void onButtonClicked(View v) {
		Log.d("RemoteActivity", "Got click from  :" + v.getTag());
		String myTag = (String) v.getTag();
		for (PytoDevice dev : myDevices) {
			if (dev.getDevID().equalsIgnoreCase(myTag)) {
				// netFrag.setPytoServerDetails(hostname, user, pass);
				Log.d("RemoteActivity", "Found Device doCommand");
				if (dev.getDevState().equalsIgnoreCase("off")) {
					doCommand(myTag, "on");

				} else {
					doCommand(myTag, "off");
				}

			}

		}

	}

	public void onButtonLongClicked(View v, String command) {
		Log.d("RemoteActivity", "Got click from  :" + v.getTag());
		String myTag = (String) v.getTag();
		for (PytoDevice dev : myDevices) {
			if (dev.getDevID().equalsIgnoreCase(myTag)) {
				// netFrag.setPytoServerDetails(hostname, user, pass);
				doCommand(myTag, command);

			}

		}

	}

	public void startProgressBar() {
		dialog = new ProgressDialog(this);
		dialog.setIndeterminate(true);
		dialog.setCancelable(false);
		dialog.setMessage("Talking to your pytomation server! Please wait...!");
		dialog.show();
	}
	
	public void showServerAlert()
	{
		AlertDialog alertDialog = new AlertDialog.Builder(this)
		.create();
alertDialog.setTitle("Can't Connect to server!");
alertDialog
		.setMessage("Check your server details under settings");
alertDialog.setButton("OK",
		new DialogInterface.OnClickListener() {
			public void onClick(DialogInterface dialog,
					int which) {}
		});
// Set the Icon for the Dialog
alertDialog.show();
	
	}
	
	@Override
	public void onStop(){
		super.onStop();
		PyHomeController.getInstance().getRequestQueue().cancelAll(statusTag);
		PyHomeController.getInstance().cancelPendingRequests(commandTag);
		if (handler!=null){
		handler.removeCallbacksAndMessages(null);
		}
	}
	public void onDestroy(){
		super.onDestroy();
		PyHomeController.getInstance().cancelPendingRequests(statusTag);
		PyHomeController.getInstance().cancelPendingRequests(commandTag);
		if (handler!=null){
		handler.removeCallbacksAndMessages(null);}
	}

	// don't want to parse the JSON too often - too many damn try catches
	public void parseMyDevices(String result) {
		SharedPreferences sharedP = getSharedPreferences("pyto_data", 0);
		Editor editor = sharedP.edit();
		editor.putString("json_data", result).commit();
		myDevices = new ArrayList<PytoDevice>();

		JSONArray jsa;
		try {
			jsa = new JSONArray(result);

			Log.d("RemoteActivity", "got json :  " + jsa.length());
			for (int i = 0; i < jsa.length(); i++) {
				PytoDevice curDevice = new PytoDevice(jsa.getJSONObject(i));
				if (curDevice.getDevType().equalsIgnoreCase("Light")) {
					myDevices.add(curDevice);
				}
				Log.d("RemoteActivity",
						"parseMyDevices " + curDevice.toString());
			}
		} catch (JSONException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}

		createRemotePanel();

	}

	
	public void onResume() {
		super.onResume();
		Log.d("RemoteActivity", "resuming");
		SharedPreferences sharedP = getSharedPreferences("pyto_data", 0);
		String jsonData = sharedP.getString("json_data", null);
		readHostCredentials();
		if (hostname!=null){
		getDevices();}
		if (jsonData!=null){
		this.parseMyDevices(jsonData);
		}
		createRemotePanel();

	}

	private void getDevices() {
		Log.d("RemoteActivity", "Get Devices URL = " + hostname + "/api/devices");
		JsonArrayRequest req = new JsonArrayRequest(hostname + "/api/devices",
				new Response.Listener<JSONArray>() {
					@Override
					public void onResponse(JSONArray response) {
						if (dialog != null && dialog.isShowing()) {
							dialog.dismiss();
						}
						Log.d("RemoteActivity",
								"Get Devices " + response.toString());
						parseMyDevices(response.toString());
					    handler = new Handler();
						Runnable scheduledUpdate = new Runnable() {
							@Override
							public void run() {
								getDevices();
							}

						};
						handler.postDelayed(scheduledUpdate, refreshRate);
						// pDialog.hide();
					}
				}, new Response.ErrorListener() {
					@Override
					public void onErrorResponse(VolleyError error) {
						
						Log.d("RemoteActivity", "Error: " + error.getMessage());
						if (dialog != null && dialog.isShowing()) {
							dialog.dismiss();
						}
						showServerAlert();
					}

				}) {
			@Override
			public Map<String, String> getHeaders() throws AuthFailureError {
				HashMap<String, String> headers = new HashMap<String, String>();
				String authString = user + ":" + pass;
				String encodedPass = null;
				try {
					encodedPass = Base64.encodeToString(authString.getBytes(),
							Base64.DEFAULT);
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				Log.d("Remote Activity", pass + " " + encodedPass);
				headers.put("Content-Type", "application/json");
				headers.put("Authorization", "Basic " + encodedPass);
				return headers;
			}
		};
		req.setRetryPolicy(new DefaultRetryPolicy(
                20000, 
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES, 
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT)); 
	
		PyHomeController.getInstance().addToRequestQueue(req, statusTag);

	}

	private void doCommand(String myTag, String command) {
		final String curCommand = command;
		final String curTag = myTag;
		HashMap<String, String> params = new HashMap<String, String>();
		params.put("command=", "off");
		Log.d("RemoteActivity", "doCommand:" + hostname + "/api/device/"
				+ myTag + " " + params.toString());
		JsonObjectRequest req = new JsonObjectRequest(Method.POST, hostname
				+ "/api/device/" + myTag, null,
				new Response.Listener<JSONObject>() {

					@Override
					public void onResponse(JSONObject response) {
						if (dialog != null && dialog.isShowing()) {
							dialog.dismiss();
						}
						Log.d("RemoteActivity",
								"doCommand" + response.toString());
						for (PytoDevice dev : myDevices) {
							View myView = remoteFrag.getView().findViewWithTag(
									curTag);
							if (dev.getDevID().equalsIgnoreCase(curTag)) {
								try {

									String devState = response
											.getString("state");
									dev.setDevState(devState);
									if (devState.equalsIgnoreCase("on")) {
										myView.setBackgroundResource(R.drawable.light_bulb_on);
									} else {
										if (devState.equalsIgnoreCase("off")) {
											myView.setBackgroundResource(R.drawable.light_bulb_off);
										} else {
											myView.setBackgroundResource(R.drawable.light_bulb_dimmed);
										}
									}

								} catch (JSONException e) {
									// TODO Auto-generated catch block
									e.printStackTrace();
								}
							}
						}
						// pDialog.hide();
					}
				}, new Response.ErrorListener() {

					@Override
					public void onErrorResponse(VolleyError error) {
						Log.d("RemoteActivity",
								"doCommand Error: " + error.getMessage());
						// pDialog.hide();
					}
				}) {
			@Override
			public Map<String, String> getHeaders() throws AuthFailureError {
				HashMap<String, String> headers = new HashMap<String, String>();
				String authString = user + ":" + pass;
				String encodedPass = null;
				try {
					encodedPass = Base64.encodeToString(authString.getBytes(),
							Base64.DEFAULT);
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				Log.d("Remote Activity", pass + " " + encodedPass);
				// headers.put("Content-Type", "application/json");
				headers.put("Authorization", "Basic " + encodedPass);
				return headers;
			}

			@Override
			public byte[] getBody() {
				// Map<String, String> params = new HashMap<String, String>();
				// params.put("command", "on");
				// params.put("email", "abc@androidhive.info");
				// params.put("password", "password123");
				String params = "command=" + curCommand;
				return params.getBytes();
			}

		};

		PyHomeController.getInstance().addToRequestQueue(req,commandTag);
	}

	private void createRemotePanel() {
		PytoDevice[] pDevs = null;
		if (myDevices!=null){
		pDevs = (PytoDevice[]) myDevices
				.toArray(new PytoDevice[myDevices.size()]);
		}
		getFragmentManager()
				.beginTransaction()
				.replace(R.id.container,
						remoteFrag = RemotePanelFragment.newInstance(pDevs))
				.commit();
	}

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_remote);
		myApp = (PyHomeController) getApplication();

		final ActionBar actionBar = getActionBar();
		actionBar.setDisplayShowTitleEnabled(false);
		actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_LIST);
		actionBar.setListNavigationCallbacks(
		// Specify a SpinnerAdapter to populate the dropdown list.
				new ArrayAdapter<String>(actionBar.getThemedContext(),
						android.R.layout.simple_list_item_1,
						android.R.id.text1, new String[] { "All" }), this);

	}

	@Override
	public void onRestoreInstanceState(Bundle savedInstanceState) {
		// Restore the previously serialized current dropdown position.
		Log.d("RemoteActivity", "onRestoreInstanceState");
		if (savedInstanceState.containsKey(STATE_SELECTED_NAVIGATION_ITEM)) {
			getActionBar().setSelectedNavigationItem(
					savedInstanceState.getInt(STATE_SELECTED_NAVIGATION_ITEM));
		}
	}

	@Override
	public void onSaveInstanceState(Bundle outState) {
		// Serialize the current dropdown position.
		outState.putInt(STATE_SELECTED_NAVIGATION_ITEM, getActionBar()
				.getSelectedNavigationIndex());
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {

		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.remote, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		// Handle action bar item clicks here. The action bar will
		// automatically handle clicks on the Home/Up button, so long
		// as you specify a parent activity in AndroidManifest.xml.
		int id = item.getItemId();
		if (id == R.id.action_settings) {
			Intent intent = new Intent();
			intent.setClass(RemoteActivity.this, SettingsActivity.class);
			startActivityForResult(intent, 0);

			return true;
		}
		if (id == R.id.Status) {
			readHostCredentials();
			if (handler!=null){
				handler.removeCallbacksAndMessages(null);
			}
			getDevices();
			startProgressBar();
		}
		return super.onOptionsItemSelected(item);
	}

	@Override
	public boolean onNavigationItemSelected(int position, long id) {
		// When the given dropdown item is selected, show its contents in the
		// container view.
		String instanceString = "nodata";
		if (myDevices != null) {
			Log.d("RemoteActivity", myDevices.get(0).getClass().toString());
			PytoDevice[] pDevs = (PytoDevice[]) myDevices
					.toArray(new PytoDevice[myDevices.size()]);

		} else {

			getFragmentManager()
					.beginTransaction()
					.replace(
							R.id.container,
							remoteFrag = RemotePanelFragment
									.newInstance(instanceString)).commit();
		}
		return true;
	}

	protected void readHostCredentials() {
		SharedPreferences settings = PreferenceManager
				.getDefaultSharedPreferences(this);
		hostname = settings.getString("pyto_host", null);
		user = settings.getString("pyto_user", null);
		pass = settings.getString("pyto_pass", null);
		refreshRate = 1000 * Integer.parseInt(settings.getString(
				"pyto_refresh_rate", "15"));
	}

}
