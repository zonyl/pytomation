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
    		alertDialogBuilder.setMessage("Type the exact string, ie 'level,80'");
    		final AutoCompleteTextView input = new AutoCompleteTextView(v.getContext());
    		ArrayAdapter<String> adapt = new ArrayAdapter<String>(v.getContext(),android.R.layout.select_dialog_item,COMMANDS);
    		input.setAdapter(adapt);
    		input.setMaxLines(1);
    		input.setInputType(InputType.TYPE_TEXT_FLAG_AUTO_COMPLETE);
    		input.setThreshold(0);
    		final View myView = v;
    		alertDialogBuilder.setView(input);
    		alertDialogBuilder.setPositiveButton("OK",new DialogInterface.OnClickListener() {
    			public void onClick(DialogInterface dialog, int whichButton) {
    				 
    				  command = input.getText().toString();
    				  Log.d("RemotePanel", "Command =" + command);
    				  fragListener.onButtonLongClicked(myView,command);
    					myView.setBackgroundResource(R.drawable.lightanim);	
    					AnimationDrawable lightAnimation = (AnimationDrawable) myView.getBackground();
    					lightAnimation.start();
    				  }
    				});
    		alertDialogBuilder.setNegativeButton("CANCEL",new DialogInterface.OnClickListener() {
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