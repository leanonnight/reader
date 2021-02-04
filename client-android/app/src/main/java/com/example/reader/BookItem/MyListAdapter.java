package com.example.reader.BookItem;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import com.example.reader.R;

import java.util.List;

public class MyListAdapter extends BaseAdapter {
    private List<BookData> mBookDataList;   //创建一个BookData类对象集合
    private LayoutInflater inflater;

    public  MyListAdapter (List<BookData> mBookDataList, Context context) {
        this.mBookDataList = mBookDataList;
        this.inflater = LayoutInflater.from(context);
    }


    @Override
    public int getCount() {
        return mBookDataList == null ? 0 : mBookDataList.size();  //判断有多少个Item
    }

    @Override
    public Object getItem(int i) {
        return mBookDataList.get(i);
    }

    @Override
    public long getItemId(int i) {
        return i;
    }

    @Override
    public View getView(int i, View convertView, ViewGroup viewGroup) {
        //加载布局为一个视图
        View view = inflater.inflate(R.layout.book_item,null);
        BookData mStudentData = (BookData) getItem(i);
        //在view 视图中查找 组件
        TextView tv_title = (TextView) view.findViewById(R.id.item_title);
        TextView tv_inline_block = (TextView) view.findViewById(R.id.item_inline_block);
        TextView tv_theLasterChapter = (TextView) view.findViewById(R.id.item_theLasterChapter);
        //为Item 里面的组件设置相应的数据
        tv_title.setText(mStudentData.getTitle());
        tv_inline_block.setText(mStudentData.getInline_block());
        tv_theLasterChapter.setText(mStudentData.getTheLasterChapter());
        //返回含有数据的view
        return view;
    }
}
