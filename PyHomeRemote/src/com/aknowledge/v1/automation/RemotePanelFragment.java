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





import android.app.Activity;
import android.app.AlertDialog;
import android.app.Fragment;
import android.content.DialogInterface;
import android.graphics.drawable.AnimationDrawable;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Bundle;
import android.os.Parcelable;
import android.text.InputType;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnLongClickListener;
import android.view.ViewGroup;
import android.view.View.OnClickListener;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridView;

public class RemotePanelFragment extends Fragment {

	private static final String ARG_SECTION_NAME = "sectionName";
	public ButtonAdapter buttonAdapter;
	public StateListDrawable bStates;
	public String command;
    private static final String[] COMMANDS = new String[] {
        "on", "off", "level", "status", "toggle"
    };
	
	
	onButtonClickListener fragListener;
	
	
	public interface onButtonClickListener {
		public void onButtonClicked(View v);
		public void onButtonLongClicked(View v, String command);
	}

	public void onAttach(Activity activity) {
		super.onAttach(activity);
		try {
			fragListener = (onButtonClickListener) activity;
		} catch (ClassCastException e) {
			throw new ClassCastException(activity.toString()
					+ " must implement dataClickListener");
		}
	}	
	
	
	/**
	 * Returns a new instance of this fragment for the given type This crap
	 * here is for uninitialized apps.
	 */
	public static RemotePanelFragment newInstance(String sectionName) {
		RemotePanelFragment fragment = new RemotePanelFragment();
		Bundle args = new Bundle();
		args.putString(ARG_SECTION_NAME, sectionName);
		fragment.setArguments(args);
		return fragment;
	}

	public static RemotePanelFragment newInstance(PytoDevice[] devs) {
		RemotePanelFragment fragment = new RemotePanelFragment();
		Bundle args = new Bundle();
		args.putParcelableArray("pyto_devices", devs);
		args.putString(ARG_SECTION_NAME, "all");
		fragment.setArguments(args);
		return fragment;
	}
	
	

    private OnClickListener buttonListener = new OnClickListener() {
        public void onClick(View v) {
        	Log.d("RemotePanelFrag", (String)v.getTag());
        	fragListener.onButtonClicked(v);
			v.setBackgroundResource(R.drawable.lightanim);	
			AnimationDrawable lightAnimation = (AnimationDrawable) v.getBackground();
			lightAnimation.start();
        	
        }
    };
    private OnLongClickListener buttonLongListener = new OnLongClickListener() {
    	public boolean onLongClick(View v) {
    		Log.d("REMOTEPANEL","onLongClick");
    		
    		AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(
					v.getContext());
    		alertDialogBuilder.setTitle("Enter Custom Command");
    		alertDialogBuilder.setMessage("");
    		final View myView = v;
    		
    		final View input = View.inflate(v.getContext(),R.layout.command_dialog, null);
    		
    		class myList implements OnClickListener{
    			public void onClick(View v)
    			{
    				command = "status";
    				int myID = v.getId();
    				switch (myID){
    				case R.id.on_btn: 	command = "on";
    									break;
    				case R.id.off_btn: command = "off";
    					break;
    				case R.id.low_btn: command = "level,10";
    					break;
    				case R.id.lowest_btn: command = "level,1";
    					break;
    				case R.id.med_btn: command = "level,40";
    					break;
    				case R.id.hi_btn: command = "level,70";
    				}
    				
    				
    						
    				
    				
    				Log.d("RemotePanel", "Command =" + command + v.getId());
    				  fragListener.onButtonLongClicked(myView,command);
    					myView.setBackgroundResource(R.drawable.lightanim);	
    					AnimationDrawable lightAnimation = (AnimationDrawable) myView.getBackground();
    					lightAnimation.start();
    			}
    		};
    		
    		OnClickListener variab = new myList();
    		
    		Button onBtn = (Button)input.findViewById(R.id.on_btn);
    		onBtn.setOnClickListener( variab);
    		Button offBtn = (Button)input.findViewById(R.id.off_btn);
    		offBtn.setOnClickListener(variab);
    		
    		Button statusBtn = (Button)input.findViewById(R.id.status_btn);
    		statusBtn.setOnClickListener(variab);
    		
    		Button lowestBtn = (Button)input.findViewById(R.id.lowest_btn);
    		lowestBtn.setOnClickListener(variab);
    		
    		Button lowBtn = (Button)input.findViewById(R.id.low_btn);
    		lowBtn.setOnClickListener(variab);
    		
    		Button medBtn = (Button)input.findViewById(R.id.med_btn);
    		medBtn.setOnClickListener(variab);
    		Button highBtn = (Button)input.findViewById(R.id.hi_btn);
    		highBtn.setOnClickListener(variab);
    		
    		alertDialogBuilder.setView(input);
    		alertDialogBuilder.setPositiveButton("DONE",new DialogInterface.OnClickListener() {
    			public void onClick(DialogInterface dialog, int whichButton) {
    				 }
    				});
    		
    		alertDialogBuilder.show();
    		//fragListener.onButtonLongClicked(v, command);

    		return true;
    	
    	}
    };
	
    
	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View rootView = null;
		Bundle args = getArguments();
		Parcelable[] pArray = args.getParcelableArray("pyto_devices");

		PytoDevice[] devices = (PytoDevice[]) pArray;

/**		for (int i = 0; i < devices.length; i++) {
			Log.d("RemotePanelFragment", devices[i].toString());

		}
*/
		String secName = args.getString(ARG_SECTION_NAME);
		

		
		if (secName.equalsIgnoreCase("nodata")) {
			rootView = inflater.inflate(R.layout.fragment_nodata,
					container, false);

		} else if (secName.equalsIgnoreCase("all")){
			rootView = inflater.inflate(R.layout.fragment_buttongrid,
					container, false);
			GridView gv = (GridView) rootView.findViewById(R.id.maingrid);
			buttonAdapter = new ButtonAdapter(rootView.getContext());
			buttonAdapter.setDevices(devices);
			buttonAdapter.setButtonAdapterState(bStates);
			buttonAdapter.setOnClick(buttonListener);
			buttonAdapter.setOnLongClick(buttonLongListener);
			
			buttonAdapter.setBackgroundImages(getResources().getDrawable(R.drawable.light_bulb_on), 
					getResources().getDrawable(R.drawable.light_bulb_off),
					getResources().getDrawable(R.drawable.light_bulb_unknown),
					getResources().getDrawable(R.drawable.light_bulb_dimmed));

			if(gv !=null){
				Log.d("FRAGMENT", gv.toString());
				gv.setAdapter(buttonAdapter);	
				buttonAdapter.notifyDataSetChanged();
			}
			

		}
		return rootView;
	}
}