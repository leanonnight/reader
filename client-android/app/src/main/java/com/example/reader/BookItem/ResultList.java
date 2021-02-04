package com.example.reader.BookItem;

import android.content.Context;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.LinearLayout;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.TextView;

import java.util.ArrayList;

public class ResultList extends LinearLayout {
    private static final String TAG = "reader-resultView";
    private MyListView mMyListView;
    private TextView mTextView;
    private String webName;
    private ArrayList<String> bookUrls = new ArrayList<String>();
    private static OnItemClickListener mOnItemClickListener;

    public ResultList(Context context)
    {
        this(context, null);			//调用同名构造方法
    }

    public ResultList(Context context, AttributeSet attributeSet)
    {
        this(context, attributeSet, 0);	 //调用同名构造方法
    }

    public ResultList(Context context, AttributeSet attributeSet, int defaultStyle)
    {
        //通过上面的传参，实现无论系统调用，哪个构造方法，最终调用的是具有样式的构造方法
        super(context, attributeSet, defaultStyle);
        setOrientation(LinearLayout.VERTICAL);  // 设置垂直排列
        mMyListView = new MyListView(context);
        mTextView = new TextView(context);
        mTextView.setTextSize(16);
        mTextView.setBackgroundColor(0x33dddddd);



        mMyListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                String url = bookUrls.get(i);
                mOnItemClickListener.onItemClick(url);
            }
        });
        addView(mTextView);
        addView(mMyListView);
    }

    public void setOnItemClickListener(OnItemClickListener mOnItemClickListener){
        this.mOnItemClickListener = mOnItemClickListener;
    }

    public interface OnItemClickListener{
        void onItemClick(String url);
    }

    public void setWebName(String webName){
        this.webName = webName;
        mTextView.setText("网站: " + this.webName);
    }

    public void setAdapter(ListAdapter adapter){
        mMyListView.setAdapter(adapter);
//        setListViewHeightBasedOnChildren(mMyListView);
    }

    public void addUrl(String url){
        bookUrls.add(url);
    }

    public void setResult(String webName, ListAdapter adapter){
        this.setWebName(webName + "  搜索结果: " + adapter.getCount());
        this.setAdapter(adapter);
    }

    public static void setListViewHeightBasedOnChildren(ListView listView) {
        ListAdapter listAdapter = listView.getAdapter();
        if (listAdapter == null) {
            return;
        }

        int totalHeight = 0;
        for (int i = 0; i < listAdapter.getCount(); i++) {
            View listItem = listAdapter.getView(i, null, listView);
            listItem.measure(0, 0);
            totalHeight += listItem.getMeasuredHeight();
        }

        ViewGroup.LayoutParams params = listView.getLayoutParams();
        params.height = totalHeight + (listView.getDividerHeight() * (listAdapter.getCount() - 1));
        listView.setLayoutParams(params);
    }

}
