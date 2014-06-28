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



import android.content.Context;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.StateListDrawable;
import android.util.Log;
import android.util.TypedValue;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnLongClickListener;
import android.view.ViewGroup;
import android.view.ViewGroup.LayoutParams;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.GridView;

public class ButtonAdapter extends BaseAdapter {
	private Context context;
	private PytoDevice[] pytoDevices;
	public StateListDrawable buttonStates;
	public OnClickListener oncl;
	public OnLongClickListener onlongcl;
	public Drawable onImage;
	public Drawable offImage;
	public Drawable unknownImage;
	public Drawable dimmedImage;
	
	
	public ButtonAdapter(Context c){
		context = c;

	}
	
	public void setBackgroundImages(Drawable on, Drawable off, Drawable unknownImage, Drawable dimmedImage)
	{
	this.onImage = on;
	this.offImage = off;
	this.unknownImage = unknownImage;
	this.dimmedImage = dimmedImage;
	}
	
	public void setButtonAdapterState(StateListDrawable sld){
		this.buttonStates = sld;
	}
	
	public void setOnClick(OnClickListener listener){
		this.oncl = listener;
		
	}
	public void setOnLongClick(OnLongClickListener listener){
		this.onlongcl = listener;
	}
	@Override
	public int getCount() {
		// TODO Auto-generated method stub
		return pytoDevices.length;
	}

	@Override
	public Object getItem(int arg0) {
		return pytoDevices[arg0];
		
	}

	@Override
	public long getItemId(int arg0) {
		return pytoDevices[arg0].hashCode();
		
	}

	@Override
	public View getView(int index, View arg1, ViewGroup arg2) {
		Button button;
		
        if (arg1 == null) {  // if it's not recycled, initialize some attributes
            button = new Button(context);
            final float scale = context.getResources().getDisplayMetrics().density;
            int pixels = (int) (110*scale+ 0.5f);
            //button.setLayoutParams(new GridView.LayoutParams(LayoutParams.WRAP_CONTENT,LayoutParams.WRAP_CONTENT));
            button.setLayoutParams(new GridView.LayoutParams(pixels+10,pixels-20));
         //   button.setTextSize(TypedValue.COMPLEX_UNIT_SP,12);
            
        } else {
            button = (Button) arg1;
        }

        button.setText(pytoDevices[index].getDevName());
        button.setTag(pytoDevices[index].getDevID());
      //  button.setBackgroundDrawable(buttonStates);
        button.setOnClickListener(oncl);
        button.setOnLongClickListener(onlongcl);
    //    button.setTextColor(0xFFFFFF);
     //   Log.d("WTF", pytoDevices[index].getDevState());
        if(pytoDevices[index].getDevState().equalsIgnoreCase("on")){
     
            button.setBackgroundDrawable(onImage);
  
        }else{ 
        	if (pytoDevices[index].getDevState().equalsIgnoreCase("off")) {
				button.setBackgroundDrawable(offImage);
			} else{ 
				if(pytoDevices[index].getDevState().contains("level")){
					button.setBackgroundDrawable(dimmedImage);
				}else{
				button.setBackgroundDrawable(unknownImage);
				
			}
        }
        }

        return button;
        
        
        
        
		
	}
	public void setDevices(PytoDevice[] devices) {
		if (devices== null){
			this.pytoDevices = new PytoDevice[0];
		}else{
		this.pytoDevices = devices;}
		this.notifyDataSetChanged();
		
	}

}
