package com.aknowledge.v1.automation;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.Reader;
import java.io.UnsupportedEncodingException;
import java.net.Authenticator;
import java.net.HttpURLConnection;
import java.net.PasswordAuthentication;
import java.net.URL;

import android.app.Activity;
import android.app.Fragment;
import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ProgressBar;

public class NetFragment extends Fragment {
	PytoAPITask downloadTask;
	int mPosition;

	String pytoHost;
	String pytoUser;
	String pytoPass;

	onDataLoadedListener dataListener;


	public interface onDataLoadedListener {
		public void onDevicesLoaded(String result);
		public void onCommandExecuted(View v, String result);
	}

	@Override
	public void onAttach(Activity activity) {
		super.onAttach(activity);
		try {
			dataListener = (onDataLoadedListener) activity;
		} catch (ClassCastException e) {
			throw new ClassCastException(activity.toString()
					+ " must implement onDataLoadedListener");
		}
	}

	public void setPytoServerDetails(String host, String user, String pass) {
		this.pytoHost = host;
		this.pytoUser = user;
		this.pytoPass = pass;
		Authenticator.setDefault(new Authenticator() {
			protected PasswordAuthentication getPasswordAuthentication() {
				return new PasswordAuthentication(pytoUser, pytoPass
						.toCharArray());
			}
		});

	}

	public void loadDevices() {
		String url = pytoHost + "/api/devices";
		new PytoAPITask().execute(url);

	}
	
	public void doCommand(View v, String command)
	{
		PytoAPITask pat = new PytoAPITask();
		pat.button = v;
		String url = pytoHost + "/api/device/" + (String)v.getTag();
		Log.d("NetFragment", "DoCommand:  " + url + command);
		pat.execute(url,command);
	
	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		// Tell the framework to try to keep this fragment around
		// during a configuration change.
		setRetainInstance(true);
		// Start up the worker thread.

	}

	/**
	 * This is called when the Fragment's Activity is ready to go, after its
	 * content view has been installed; it is called both after the initial
	 * fragment creation and after the fragment is re-attached to a new
	 * activity.
	 */
	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);
	}

	/**
	 * This is called when the fragment is going away. It is NOT called when the
	 * fragment is being propagated between activity instances.
	 */
	@Override
	public void onDestroy() {
		// Make the thread go away.

		super.onDestroy();
	}

	/**
	 * This is called right before the fragment is detached from its current
	 * activity instance.
	 */
	@Override
	public void onDetach() {
		// This fragment is being detached from its activity. We need
		// to make sure its thread is not going to touch any activity
		// state after returning from this function.

		super.onDetach();
	}

	/**
	 * API for our UI to restart the progress thread.
	 */
	public void restart() {

	}

	private class PytoAPITask extends AsyncTask<String, Void, String> {

		View button = null;
		protected void onPreExecute() {

		}

		@Override
		protected String doInBackground(String... urls) {
			Log.d("Download", urls[0] + Integer.toString(urls.length));
			if (urls.length == 1) {
				// params comes from the execute() call: params[0] is the url.
				try {
					
					return downloadUrl(urls[0]);
				} catch (IOException e) {
					return null;
				}

			} else {

				try {
					return postUrl(urls[0], urls[1]);
				} catch (IOException e) {
					return null;
				}
			}

		}

		@Override
		protected void onPostExecute(String result) {

		//	Log.d("PytoAPITask", result);
			if (button == null){
				dataListener.onDevicesLoaded(result);
			}else
			{
				dataListener.onCommandExecuted(button, result);
			}
			

		}

		private String downloadUrl(String myurl) throws IOException {
			InputStream is = null;
			Log.d("PytoAPITASK", "downloading " + myurl);
			try {
				URL url = new URL(myurl);
				HttpURLConnection conn = (HttpURLConnection) url
						.openConnection();
				conn.setReadTimeout(10000 /* milliseconds */);
				conn.setConnectTimeout(15000 /* milliseconds */);
				conn.setRequestMethod("GET");
				conn.setDoInput(true);
				// Starts the query
				Log.d("PytoAPITask", "about to connect");

				try {
					conn.connect();
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				Log.d("PytoAPITask", "connected");
				int response = conn.getResponseCode();
				Log.d("Lihts", "The response is: " + response);
				if (response!=200){
					return null;
				}
				is = conn.getInputStream();

				// Convert the InputStream into a string
				String contentAsString = readIt(is);
				// Log.d("LIGHTS", contentAsString);
				return contentAsString;

				// Makes sure that the InputStream is closed after the app is
				// finished using it.
			} finally {
				if (is != null) {
					is.close();
				}
			}
		}

		private String postUrl(String myurl, String command) throws IOException {
			InputStream is = null;
			try {
				URL url = new URL(myurl);
				HttpURLConnection conn = (HttpURLConnection) url
						.openConnection();
				conn.setReadTimeout(10000 /* milliseconds */);
				conn.setConnectTimeout(15000 /* milliseconds */);
				conn.setRequestMethod("POST");
				conn.setDoOutput(true);
				conn.setDoInput(true);
				conn.setRequestProperty("Content-Type", "application/json");
				conn.setRequestProperty("Accept", "application/json");
				// Starts the query
				conn.connect();
				Log.d("POST COMMAND", myurl + command);
				byte[] postData;
				try {
					postData = command.getBytes("UTF-8");
					OutputStream os = conn.getOutputStream();
					os.write(postData);
					os.close();
				} catch (UnsupportedEncodingException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				StringBuilder sb = new StringBuilder();

				int HttpResult;
				try {
					HttpResult = conn.getResponseCode();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				int response = conn.getResponseCode();
				Log.d("Lihts", "The response is: " + response);
				if (response!=200)
				{return null;}
				is = conn.getInputStream();

				// Convert the InputStream into a string
				String contentAsString = readIt(is);
				 Log.d("LIGHTS", contentAsString);
				return contentAsString;

				// Makes sure that the InputStream is closed after the app is
				// finished using it.
			} finally {
				if (is != null) {
					is.close();
				}
			}
		}

		public String readIt(InputStream stream) throws IOException,
				UnsupportedEncodingException {
			Reader reader = null;
			reader = new InputStreamReader(stream, "UTF-8");
			BufferedReader bReader = new BufferedReader(reader, 8);
			StringBuilder sb = new StringBuilder();
			String result = null;
			String line = null;
			while ((line = bReader.readLine()) != null) {
				sb.append(line + "\n");
			}
			result = sb.toString();
			return result;
		}
	}

}