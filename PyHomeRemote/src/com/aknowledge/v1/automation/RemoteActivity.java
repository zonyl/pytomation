package com.aknowledge.v1.automation;

import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.app.ActionBar;
import android.app.AlertDialog;
import android.app.Fragment;
import android.app.FragmentManager;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.graphics.drawable.AnimationDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Parcelable;
import android.preference.PreferenceManager;
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
		ActionBar.OnNavigationListener, NetFragment.onDataLoadedListener,
		RemotePanelFragment.onButtonClickListener {

	private static final String STATE_SELECTED_NAVIGATION_ITEM = "selected_navigation_item";
	// don't want to check objects and preferences too often.
	private boolean Initialized = false;

	// abstraction layer so I have even less clue what thread things run in
	NetFragment netFrag;
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

	protected void readHostCredentials() {
		SharedPreferences settings = PreferenceManager
				.getDefaultSharedPreferences(this);
		hostname = settings.getString("pyto_host", null);
		user = settings.getString("pyto_user", null);
		pass = settings.getString("pyto_pass", null);
	}

	// return from worker netFrag
	public void onDevicesLoaded(String result) {
		Log.d("RemoteActivity", "devices loaded: " + result);
		if (dialog.isShowing()) {
			dialog.dismiss();
		}
		if (result != null) {
			this.Initialized = true;
			parseMyDevices(result);
			createRemotePanel();
		} else {
			AlertDialog alertDialog = new AlertDialog.Builder(this).create();
			alertDialog.setTitle("Problems with your server info.");
			alertDialog
					.setMessage("We will now launch settings, please set your pytomation server details");
			alertDialog.setButton("OK", new DialogInterface.OnClickListener() {
				public void onClick(DialogInterface dialog, int which) {
					Intent intent = new Intent();
					intent.setClass(RemoteActivity.this, SettingsActivity.class);
					startActivityForResult(intent, 0);
				}
			});
			// Set the Icon for the Dialog
			alertDialog.show();

		}

	}

	public void onCommandExecuted(View v, String result){
		
		if (result!=null) {
			for (PytoDevice dev : myDevices) {
				if (dev.getDevID().equalsIgnoreCase((String) v.getTag())) {
					try {
						JSONObject jso = new JSONObject(result);
						String devState = jso.getString("state");
						dev.setDevState(devState);
						if ( devState.equalsIgnoreCase("on") ){
							v.setBackgroundResource(R.drawable.light_bulb_on);
						} 
						else { 
								if ( devState.equalsIgnoreCase("off")){
									v.setBackgroundResource(R.drawable.light_bulb_off);
								}
								else{
									v.setBackgroundResource(R.drawable.light_bulb_dimmed);
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
		for (PytoDevice dev : myDevices) {
			if (dev.getDevID().equalsIgnoreCase((String) v.getTag())) {
				netFrag.setPytoServerDetails(hostname, user, pass);
				if (dev.getDevState().equalsIgnoreCase("off")) {
					netFrag.doCommand(v, "command=on");

				} else {
					netFrag.doCommand(v, "command=off");
				}

			}

		}

	}

	public void onButtonLongClicked(View v, String command) {
		Log.d("RemoteActivity", "command = " + command + " View =" + v.getTag());
		for (PytoDevice dev : myDevices) {
			if (dev.getDevID().equalsIgnoreCase((String) v.getTag())) {
				netFrag.setPytoServerDetails(hostname, user, pass);
				netFrag.doCommand(v, "command=" + command);
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

		if (myDevices == null) {
			if (jsonData == null) {
				readHostCredentials();
				if (this.hostname == null) {
					AlertDialog alertDialog = new AlertDialog.Builder(this)
							.create();
					alertDialog.setTitle("No Server INFO");
					alertDialog
							.setMessage("We will now launch settings, please set your pytomation server details");
					alertDialog.setButton("OK",
							new DialogInterface.OnClickListener() {
								public void onClick(DialogInterface dialog,
										int which) {
									Intent intent = new Intent();
									intent.setClass(RemoteActivity.this,
											SettingsActivity.class);
									startActivityForResult(intent, 0);
								}
							});
					// Set the Icon for the Dialog
					alertDialog.show();

				} else {
					netFrag.setPytoServerDetails(hostname, user, pass);
					netFrag.loadDevices();
					startProgressBar();
				}

			} else {

				this.parseMyDevices(jsonData);
				createRemotePanel();

			}
		}

	}

	private void createRemotePanel() {
		PytoDevice[] pDevs = (PytoDevice[]) myDevices
				.toArray(new PytoDevice[myDevices.size()]);

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
		FragmentManager fm = getFragmentManager();
		// make sure we have a network fragment to talk to our pytomation server
		// - android cruft
		netFrag = (NetFragment) fm.findFragmentByTag("netfrag");
		if (netFrag == null) {
			Log.d("Init", "NO netFragment found");
			netFrag = new NetFragment();
			fm.beginTransaction().add(netFrag, "netfrag").commit();
		}
		// Set up the action bar to show a dropdown list.
		final ActionBar actionBar = getActionBar();
		actionBar.setDisplayShowTitleEnabled(false);
		actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_LIST);
		actionBar.setListNavigationCallbacks(
		// Specify a SpinnerAdapter to populate the dropdown list.
				new ArrayAdapter<String>(actionBar.getThemedContext(),
						android.R.layout.simple_list_item_1,
						android.R.id.text1, new String[] { "All" }), this);

		/**
		 * if (jsonData==null){
		 * netFrag.setPytoServerDetails(hostname,user,pass);
		 * netFrag.loadDevices(); startProgressBar(); return; } else{
		 * Log.d("REMOTE ACTIVITY", jsonData); parseMyDevices(jsonData); }
		 * 
		 * PytoDevice[] pDevs = (PytoDevice[]) myDevices .toArray(new
		 * PytoDevice[myDevices.size()]); Log.d("RemoteActivity",
		 * "Device Object count: " + myDevices.size()); getFragmentManager()
		 * .beginTransaction() .replace(R.id.container, remoteFrag =
		 * RemotePanelFragment.newInstance(pDevs)).commit();
		 * 
		 * readHostCredentials();
		 **/

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
			netFrag.setPytoServerDetails(hostname, user, pass);
			netFrag.loadDevices();
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

	/**
	 * Main display panel - eventually it will add room based stuff, but only
	 * implemented ALL room for now
	 */

}
