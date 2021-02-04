package com.example.reader.BookItem;

import android.content.Context;
import android.util.AttributeSet;
import android.util.Log;
import android.widget.ListView;


//用来解决Scroll与ListView冲突
public class MyListView extends ListView {
    private static final String TAG = "reader-MyListView";
    private int height = 0;
    public MyListView(Context context)
    {
        super(context);
        // TODO Auto-generated constructor stub
    }

    public MyListView(Context context, AttributeSet attrs)
    {
        super(context, attrs);
        // TODO Auto-generated constructor stub
    }

    public MyListView(Context context, AttributeSet attrs, int defStyle)
    {
        super(context, attrs, defStyle);
        // TODO Auto-generated constructor stub
    }

    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec)
    {
        int expandSpec = MeasureSpec.makeMeasureSpec(Integer.MAX_VALUE >> 2, MeasureSpec.AT_MOST);
        height = expandSpec;
        super.onMeasure(widthMeasureSpec, expandSpec);
    }

    public int getMyHeight() {
        return height;
    }

    public void setMyHeight(int height){
        this.height = height;
    }

}