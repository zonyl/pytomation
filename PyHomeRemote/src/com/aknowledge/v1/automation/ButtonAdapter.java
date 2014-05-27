package com.aknowledge.v1.automation;



import android.content.Context;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.StateListDrawable;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
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
	public Drawable onImage;
	public Drawable offImage;
	public Drawable unknownImage;
	
	
	public ButtonAdapter(Context c){
		context = c;

	}
	
	public void setBackgroundImages(Drawable on, Drawable off, Drawable unknownImage)
	{
	this.onImage = on;
	this.offImage = off;
	this.unknownImage = unknownImage;
	}
	
	public void setButtonAdapterState(StateListDrawable sld){
		this.buttonStates = sld;
	}
	
	public void setOnClick(OnClickListener listener){
		this.oncl = listener;
		
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
            button.setLayoutParams(new GridView.LayoutParams(LayoutParams.WRAP_CONTENT,LayoutParams.WRAP_CONTENT));
          

        } else {
            button = (Button) arg1;
        }

        button.setText(pytoDevices[index].getDevName());
        button.setTag(pytoDevices[index].getDevID());
      //  button.setBackgroundDrawable(buttonStates);
        button.setOnClickListener(oncl);

        if(pytoDevices[index].getDevState().equalsIgnoreCase("on")){
            Log.d("WTF", pytoDevices[index].getDevState());
            button.setBackgroundDrawable(onImage);
  
        }else{ 
        	if (pytoDevices[index].getDevState().equalsIgnoreCase("off")) {
				button.setBackgroundDrawable(offImage);
			} else{
				button.setBackgroundDrawable(unknownImage);
				
			}
        }

        return button;
        
        
        
        
		
	}
	public void setDevices(PytoDevice[] devices) {
		this.pytoDevices = devices;;
		this.notifyDataSetChanged();
		
	}

}
