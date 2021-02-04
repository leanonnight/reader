package com.example.reader;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.Window;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.example.reader.BookItem.BookData;
import com.example.reader.BookItem.MyListAdapter;
import com.example.reader.BookItem.ResultList;

import java.util.ArrayList;
import java.util.List;

//import static com.example.reader.SocketService.SOCKET_CMD_RECV;
//import static com.example.reader.SocketService.SOCKET_CMD_SEND;

public class SearchBookActivity extends AppCompatActivity{

    private static final String TAG = "reader-SeBookActivity";
    private SearchBookBroadcastRecv searchBookBroadcastRecv = new SearchBookBroadcastRecv();
    private ImageButton mSearchBtn;
    private ImageButton mBackBtn;
    private EditText mEditText;
//    private ListView mListView;
    private LinearLayout mLinearLayout;
    private TextView mShowInfoTextView;
    private String mShowInfoString;
    private CircleProgressBar mCircleProgressBar;
    private ArrayList<String> bookUrls = null;
    private ResultList mResultView;
    public Toast toast = null;
    private int chapterNum = 0;
    private int bookSize = 0;
    private String bookName = null;
    boolean isStartCrawlBook = false;
    private Handler handler = null;
    private Lock processDataThreadLock = new Lock();

    void showToast(String msg){

        if(toast != null){
            toast.setText(msg);
            toast.setDuration(Toast.LENGTH_SHORT);
            toast.show();
        }else{
            toast = Toast.makeText(this,msg,Toast.LENGTH_SHORT);
            toast.show();
        }
    }

    void showToast(String msg,int duration){

        if(toast != null){
            toast.setText(msg);
            toast.setDuration(duration);
            toast.show();
        }else{
            toast = Toast.makeText(this,msg,duration);
            toast.show();
        }
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        supportRequestWindowFeature(Window.FEATURE_NO_TITLE);//去除标题
        setContentView(R.layout.activity_search_book);

        mSearchBtn = (ImageButton) findViewById(R.id.Search_SearchBtn);
        mBackBtn = (ImageButton) findViewById(R.id.Search_BackBtn);
        mEditText = (EditText) findViewById(R.id.Search_EditText);
        mLinearLayout = (LinearLayout) findViewById(R.id.Search_LinearLayout);
        mCircleProgressBar = (CircleProgressBar) findViewById(R.id.Search_CircleProgressbar);
        mShowInfoTextView = (TextView) findViewById(R.id.Search_ShowInfoTV);

        /**
         * 设置TextView自动滑动
         */
        mShowInfoTextView.setMovementMethod(ScrollingMovementMethod.getInstance());

        //先隐藏mLinearLayout和mCircleProgressBar
//        mLinearLayout.setVisibility(View.INVISIBLE);
        mCircleProgressBar.setVisibility(View.INVISIBLE);
        mShowInfoTextView.setVisibility(View.INVISIBLE);

        SocketRegisterReceiver();
//        UpdateBookList(null);
        //搜索书籍
        mSearchBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //关闭键盘（比如输入结束后执行）
                InputMethodManager imm =(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
                imm.hideSoftInputFromWindow(mEditText.getWindowToken(), 0);

                String data = mEditText.getText().toString();
                String temp = "$1," + data + "#";
                SendBrodacastToSocketService(temp);
                mLinearLayout.removeAllViews();
                bookUrls = new ArrayList<String>();
                mCircleProgressBar.setVisibility(View.INVISIBLE);
                mShowInfoTextView.setVisibility(View.INVISIBLE);
            }
        });

        //软键盘回车按钮等同于搜索按钮
        mEditText.setOnKeyListener(new View.OnKeyListener() {
            @Override
            public boolean onKey(View v, int keyCode, KeyEvent event) {
                if (keyCode == KeyEvent.KEYCODE_ENTER) {// 监听到回车键，会执行2次该方法。按下与松开
                    if (event.getAction() == KeyEvent.ACTION_DOWN) {//按下事件
                        //关闭键盘（比如输入结束后执行）
                        InputMethodManager imm =(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
                        imm.hideSoftInputFromWindow(mEditText.getWindowToken(), 0);

                        String data = mEditText.getText().toString();
                        String temp = "$1," + data + "#";
                        SendBrodacastToSocketService(temp);
                        mLinearLayout.removeAllViews();
                        bookUrls = new ArrayList<String>();
                        mCircleProgressBar.setVisibility(View.INVISIBLE);
                        mShowInfoTextView.setVisibility(View.INVISIBLE);
                    }
                }
                return false;
            }
        });

        mResultView = new ResultList(getApplicationContext());
        mResultView.setOnItemClickListener(new ResultList.OnItemClickListener() {
            @Override
            public void onItemClick(String url) {
                isStartCrawlBook = true;//将开始爬取标志设为true
//                Log.e(TAG, "onItemClick: mResultView");
                String data = "$2," + url + ",#";
                SendBrodacastToSocketService(data);

                //mListView设置为不可见
                mLinearLayout.setVisibility(View.INVISIBLE);
                //mCircleProgressBar、mShowInfoTextView设置为可见
                mCircleProgressBar.progressInit();
                mCircleProgressBar.setVisibility(View.VISIBLE);
                mShowInfoTextView.setVisibility(View.VISIBLE);
            }
        });


        //返回上一页
        mBackBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                finish();
            }
        });

//        //选择爬取的网站
//        mLinearLayout.setOnItemClickListener(new AdapterView.OnItemClickListener() {
//            @Override
//            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
//                String url = bookUrls.get(i);
//                String data = "$2," + url + ",#";
//                SendBrodacastToSocketService(data);
//
//                //mListView设置为不可见
//                mLinearLayout.setVisibility(View.INVISIBLE);
//                //mCircleProgressBar、mShowInfoTextView设置为可见
//                mCircleProgressBar.progressInit();
//                mCircleProgressBar.setVisibility(View.VISIBLE);
//                mShowInfoTextView.setVisibility(View.VISIBLE);
//            }
//        });
        new ProcessDataThread().start();
    }

    public class ProcessDataThread extends Thread{
        @Override
        public void run() {
            super.run();
            try {
                processDataThreadLock.lock();
                while(true){
                    processDataThreadLock.lock();
                    Log.e(TAG, "ProcessData run");
                    float comDataSize = (float)(Math.round( Buff.buff.length/1024/1024*100)/100);
                    byte[] decomData = MyFile.decompress(Buff.buff); // 解压被压缩的数据
                    Log.e(TAG, new String(decomData));
                    Log.e(TAG, "ProcessData decomData");
                    float decomDataSize = (float)(Math.round( decomData.length/1024/1024*100)/100);
                    try {
                        TextViewAppend("《" + bookName + "》"+ " 下载完成," + "压缩文件大小:" + comDataSize + "M,解压后文件大小:" + decomDataSize + "M\r\n");

                        String path = new MyFile(getApplicationContext()).saveFileToSDcard(bookName + ".txt",decomData);
                        TextViewAppend("《" + bookName + "》"+ "存储在:" + path + "\r\n");
                        showToast("《" + bookName + "》"+ " 下载完成");
                        Log.e(TAG, bookName + "保存完成" + " 书籍大小:" + decomDataSize + "M");
                        isStartCrawlBook = false;
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }

            } catch (InterruptedException e) {
                e.printStackTrace();
            }

        }
    }

    /**
     * 广播
     */
    public class SearchBookBroadcastRecv extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            //在这里写上相关的处理代码，一般来说，不要此添加过多的逻辑或者是进行任何的耗时操作
            //因为广播接收器中是不允许开启多线程的，过久的操作就会出现报错
            //因此广播接收器更多的是扮演一种打开程序其他组件的角色，比如创建一条状态栏通知，或者启动某个服务
            if(intent.getAction().equals(SocketService.SOCKET_CMD_RECV)){
                int dataType = intent.getIntExtra("dataType",0);
                String data = intent.getStringExtra("data");
                if(dataType == SocketService.dataType_bookList){//数据类型为 "书单"
                    if (!isStartCrawlBook){ // 如果开始爬取书籍 则不再添加书单
                        addResultView(data);
                    }
                }else if(dataType == SocketService.dataType_chapterContent){//数据类型为 "小说内容"
                    Log.e(TAG, "SocketService.dataType_chapterContent");
                    processDataThreadLock.unlock();
//                    float comDataSize = (float)(Math.round( Buff.buff.length/1024/1024*100)/100);
//
//                    byte[] decomData = MyFile.decompress(Buff.buff); // 解压被压缩的数据
//
//                    float decomDataSize = (float)(Math.round( decomData.length/1024/1024*100)/100);
//                    try {
//                        TextViewAppend("《" + bookName + "》"+ " 下载完成," + "压缩文件大小:" + comDataSize + "M,解压后文件大小:" + decomDataSize + "M\r\n");
//
//                        String path = new MyFile(getApplicationContext()).saveFileToSDcard(bookName + ".txt",decomData);
//                        TextViewAppend("《" + bookName + "》"+ "存储在:" + path + "\r\n");
//                        showToast("《" + bookName + "》"+ " 下载完成");
//                        Log.e(TAG, bookName + "保存完成" + " 书籍大小:" + decomDataSize + "M");
//                        isStartCrawlBook = false;
//                    } catch (Exception e) {
//                        e.printStackTrace();
//                    }
//                    writeFileData(bookName + ".txt",  Buff.buff); // 写入文件
                }else if(dataType == SocketService.dataType_crawlProgress){//数据类型为 "进度"
                    int progress = Integer.valueOf(data);
                    mCircleProgressBar.progressUpdata(progress + "/" + chapterNum,chapterNum,progress);
                }else if(dataType == SocketService.dataType_chapterNum){//数据类型为 "章节数"
                    chapterNum = Integer.valueOf(data);
                    mCircleProgressBar.progressUpdata("0/" + chapterNum,chapterNum,0);
                }else if(dataType == SocketService.dataType_info){//数据类型为"信息"
                    TextViewAppend(data + "\r\n");
                }else if(dataType == SocketService.dataType_bookSize){//数据类型为“书籍大小”
                    bookSize  = Integer.valueOf(data);
                    mCircleProgressBar.progressUpdata("0/" + bookSize/1024 + "K",bookSize/1024,0);
                }else if(dataType == SocketService.dataType_downloadProgress){//数据类型为“书籍下载进度”
                    int downloadProgress  = Integer.valueOf(data);
                    mCircleProgressBar.progressUpdata(downloadProgress/1024 + "/" + bookSize/1024 + "K",bookSize/1024,0);
                }else if(dataType == SocketService.dataType_error){//数据类型为 “爬取过程中的错误”
                    TextViewAppend("error:" + data + "\r\n");
                }else if(dataType ==SocketService.dataType_bookName){//数据类型为 “书籍名称”
                    bookName = data;
                }

            }

        }
    }

    void handleSendMessage(int what,String data){
        Message message = new Message();
        message.what = what;
        Bundle bundle = new Bundle();
        bundle.putString("data",data);
        message.setData(bundle);
        handler.sendMessage(message);
    }


    private void TextViewAppend(String data){
        mShowInfoTextView.append(data);
        //自动滑动到最新数据
        int scrollAmount = mShowInfoTextView.getLayout().getLineTop(mShowInfoTextView.getLineCount())
                - mShowInfoTextView.getHeight();
        if (scrollAmount > 0)
            mShowInfoTextView.scrollTo(0, scrollAmount);
        else
            mShowInfoTextView.scrollTo(0, 0);
    }

    private void addResultView(String data){
        String resultRegex = "'webName': '(.*?)', 'resultList': \\[(.*)\\]";  //正则表达式
        Pattern resultPattern = Pattern.compile(resultRegex);
        Matcher matcherJson = resultPattern.matcher(data);
        if(matcherJson.find()){
            String webName = matcherJson.group(1);
            String bookListJson = matcherJson.group(2);
            ArrayList<String> bookList = ParseBookList(bookListJson);
            addBookList(bookList, webName);
        }
    }

    private ArrayList<String> ParseBookList(String data){
        Pattern jsonPattern = Pattern.compile("\\{(.*?)\\}");
        Matcher matcherJson = jsonPattern.matcher(data);
        ArrayList<String> bookList = new ArrayList<String>();
        while(matcherJson.find()){
            bookList.add(matcherJson.group(0));
        }
        return bookList;
    }

    private void addBookList(ArrayList<String> bookList, String webName){
        mLinearLayout.setVisibility(View.VISIBLE);
        ResultList resultView = new ResultList(this);
        String regex = "'title': '(.*?)', 'href': '(.*?)', 'inline_block': '(.*?)', 'theLasterChapter': '(.*?)', 'coverImgUrl': '(.*?)'";  //正则表达式
        Pattern bookPattern = Pattern.compile(regex);
        List<BookData> mBookDataList = new ArrayList<>();  //创建studentData 对象集合
        for( int i = 0; i < bookList.size() ; i++) {
            Matcher matcherJson = bookPattern.matcher(bookList.get(i));
            if(matcherJson.find()){
//                Log.e(TAG, "addBookList: " + matcherJson.group(0));
                BookData mBookData = new BookData();      //循环创建studentData 对象
                mBookData.setTitle(matcherJson.group(1));
                resultView.addUrl(matcherJson.group(2));
                mBookData.setInlineBlock(matcherJson.group(3));
                mBookData.setTheLasterChaoter(matcherJson.group(4));
                mBookDataList.add(mBookData);                  //将对象添加到列表中
            }else{
                Log.e(TAG, "UpdateBookList: 未匹配");
            }
        }
        //创建Adapter 实例化对象， 调用构造函数传参，将数据和adapter  绑定
        MyListAdapter mMyListAdapter = new MyListAdapter(mBookDataList,this);
        resultView.setResult(webName, mMyListAdapter);
        mLinearLayout.addView(resultView);
//        ListView.setAdapter(mMyListAdapter);   //将定义的adapter 和 listView 绑定
    }

    public void SendBrodacastToSocketService(String data){
        Intent intent = new Intent();
        intent.setAction(SocketService.SOCKET_CMD_SEND);
        intent.putExtra("data",data);
        //注册发送数据广播
        sendBroadcast(intent);
    }

    //注册广播 与服务组件进行通信
    public void SocketRegisterReceiver(){
        IntentFilter intentFilter = new IntentFilter();
        intentFilter.addAction(SocketService.SOCKET_CMD_RECV);
        //注册发送数据广播
        registerReceiver(searchBookBroadcastRecv,intentFilter);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(searchBookBroadcastRecv);
    }

}
