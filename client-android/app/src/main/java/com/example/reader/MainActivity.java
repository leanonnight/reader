package com.example.reader;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.icu.text.UnicodeSetIterator;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;

public class MainActivity extends AppCompatActivity {

  private static final String TAG = "reader-MainActivity";
  private SocketServiceBroadcast socketServiceBroadcast = new SocketServiceBroadcast();
  private Toast toast = null;

  @Override
  protected void onDestroy() {
    super.onDestroy();
    unregisterReceiver(socketServiceBroadcast);
  }

  /**
   * 添加菜单
   */
  @Override
  public boolean onCreateOptionsMenu(Menu menu) {
    getMenuInflater().inflate(R.menu.main,menu);
    return true;
  }
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
  /**
   * 菜单栏选中事件
   */
  @Override
  public boolean onOptionsItemSelected(@NonNull MenuItem item) {
    String s = item.getTitle().toString();

    if(s.equals(getString(R.string.menu_title))){
      Log.e(TAG, "R.id.menu_menu:" + s);
    }else if(s.equals(getString(R.string.menu_search_title))){
      Log.e(TAG, "R.id.menu_search:" + s);
      Intent intent = new Intent(this,SearchBookActivity.class);
      startActivity(intent);  //开始跳转
    }
    return super.onOptionsItemSelected(item);
  }

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    Log.e(TAG, "onCreate: start" );
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    SocketRegisterReceiver();
    /**
     * 开启socket服务
     */
    Intent intent = new Intent(this,SocketService.class);
    startService(intent);  //开启服务

  }

  /**
   * 广播
   */
  public class SocketServiceBroadcast extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
      //在这里写上相关的处理代码，一般来说，不要此添加过多的逻辑或者是进行任何的耗时操作
      //因为广播接收器中是不允许开启多线程的，过久的操作就会出现报错
      //因此广播接收器更多的是扮演一种打开程序其他组件的角色，比如创建一条状态栏通知，或者启动某个服务
      if(intent.getAction().equals(SocketService.SOCKET_INFO)){
        int infoType = intent.getIntExtra("infoType",0);
        String data = intent.getStringExtra("data");
        if(infoType == SocketService.infoType_toast){
          showToast(data);
        }
      }

    }
  }

  //注册广播 与服务组件进行通信
  public void SocketRegisterReceiver(){
    IntentFilter intentFilter = new IntentFilter();
    intentFilter.addAction(SocketService.SOCKET_INFO);
    //注册发送数据广播
    registerReceiver(socketServiceBroadcast,intentFilter);
  }


}
