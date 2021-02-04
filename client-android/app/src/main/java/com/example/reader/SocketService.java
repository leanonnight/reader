package com.example.reader;

import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;

import java.util.ArrayList;
import java.util.TimerTask;

public class SocketService extends Service {
    private final String TAG = "reader-SocketService";
    private Socket socket = new Socket();
//    private String IP_ADDRESS = "192.168.43.65";
//    private String IP_ADDRESS = "192.168.137.1";
//    private String IP_ADDRESS = "10.203.11.132";
    private String IP_ADDRESS = "47.100.181.152";
//    private String IP_ADDRESS = "192.168.1.2";
    private int PORT = 9999;
    private InputStream inputStream;
    private OutputStream outputStream;
    private SocketBroadcastRecv socketBroadcastRecv = new SocketBroadcastRecv();

    public static final String SOCKET_CMD_RECV = "android.intent.action.ACTION_SOCKET_CMD_RECV";
    public static final String SOCKET_CMD_SEND = "android.intent.action.ACTION_SOCKET_CMD_SEND";
    public static final String SOCKET_INFO = "android.intent.action.ACTION_SOCKET_INFO";

    public static final int dataType_bookList = 1;   // 书单
    public static final int dataType_chapterContent = 2;  // 小说内容
    public static final int dataType_crawlProgress = 3;   // 爬取进度
    public static final int dataType_chapterNum = 4;  // 章节数
    public static final int dataType_bookSize = 5;   // 小说大小
    public static final int dataType_error = 6;  // 爬取出错
    public static final int dataType_info = 7;  // 爬取过程中的消息
    public static final int dataType_downloadProgress = 8;  //下载进度
    public static final int dataType_bookName = 9;  //书籍名称

    public static final int infoType_toast = 1;


    private boolean isStartRecvData = false; //是否开始接收数据标志
    private boolean isStartSendData = false; //是否发送数据标志
    private static int MAX_RECVBUFF_LEN = 52428800;  //50兆
    private byte[] recvBuff = new byte[MAX_RECVBUFF_LEN];
    private byte[] sendBuff;


    private int OnePercentProgress = MAX_RECVBUFF_LEN / 100;/*每百分之一进度*/
    private int recvBuffIndex = 0;
    private int currentRecvBuffIndex = 0;
    private int currentRecvNum = 0;
    private int recvBuffLen = 0;
    private int percent;
    private int recvDataType = 0;    //此次接收数据类型
    boolean socketRecvLock = true;
//    private Condition condition = new ReentrantLock().newCondition();
    private Lock timerLock = new Lock();
    private Timer timer = new Timer();

    public class Timer extends Thread{
        @Override
        public void run() {
            super.run();
            while(true){
                try {
                    timerLock.unlock();
                    sleep(100); // 0.1s
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }



    /**
     * 更新进度的回调接口
     */
    private OnDataListener onDataListener;


    /**
     * 注册回调接口的方法，供外部调用
     * @param onDataListener
     */
    public void setOnDataListener(OnDataListener onDataListener) {
        this.onDataListener = onDataListener;
    }

    /**
     * 回调接口
     */
    public interface OnDataListener {
        void onDataListener(int recvDataType,String data);
    }

    /**
     * 返回一个Binder对象
     */
    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        return new DataBinder();
    }

    public class DataBinder extends Binder {
        /**
         * 获取当前Service的实例
         * @return
         */
        public SocketService getService(){
            return SocketService.this;
        }
    }



    //连接服务器
    public class ConnectServerThread extends Thread{
        @Override
        public void run() {
            super.run();
            try{
                SocketAddress socketAddress = new InetSocketAddress(IP_ADDRESS,PORT);
                socket.connect(socketAddress,5000);
                socket.setReceiveBufferSize(1048576);
                Log.e(TAG, "ReceiveBufferSize:" + socket.getReceiveBufferSize());
                SendSocketInfoBroadcast(infoType_toast,"服务器连接成功");
                Log.e(TAG, "服务器连接成功");
            }catch(IOException e){
                SendSocketInfoBroadcast(infoType_toast,"服务器连接失败");
                Log.e(TAG, "服务器连接失败");
                e.printStackTrace();
            }
            //绑定套接字的输入输出流
            try{
                inputStream = socket.getInputStream();
                outputStream = socket.getOutputStream();
                /*
                   登录（只有在刚登录时发送登录命令("$-#") 才不会被服务器强制下线）
                 */
                outputStream.write("$-#".getBytes());
                outputStream.flush();

                //开启线程
                new SocketRecvThread().start();
                new SocketSendData().start();

                Log.e(TAG, "套接字I/OStream绑定成功");
            }catch(IOException e){
                Log.e(TAG, "套接字I/OStream绑定失败");
                e.printStackTrace();
            }
        }
    }


    //接收socket数据
    class SocketRecvThread extends Thread{
        int recvAmount = 0;
        @Override
        public void run() {
            super.run();
            while(true){
                try {
                    Log.e(TAG, "inputStream:" + inputStream.available());
                    Log.e(TAG, "recvBuffIndex" + recvBuffIndex);
                    currentRecvNum = inputStream.read(recvBuff, recvBuffIndex, 65535);
                    recvBuffIndex += currentRecvNum;
                    recvAmount += currentRecvNum;
                    Log.e(TAG, "currentRecvNum:" + currentRecvNum + " recvBuffIndex:" + recvBuffIndex + " recvAmount:" + recvAmount);
                    if(currentRecvNum == -1){
                        Log.e(TAG, "Socket连接断开");
                        SendSocketInfoBroadcast(infoType_toast,"Socket连接断开");
                        SendSocketCmdBroadcast(dataType_info,"Socket连接断开");
                        break;
                    }
                    if(isStartRecvData == false){
                        if(recvBuff[0] != '$'){
                            recvBuffIndex = 0;
//                            Log.e(TAG, "1");
                            continue;
                        }
                        if(currentRecvNum >= 14){
                            //数据长度 $1,xxxxxxxxxx,
                            recvBuffLen = Integer.valueOf(new String(recvBuff,currentRecvBuffIndex+3,10));
                            recvDataType = recvBuff[1] - '0';
                            Log.e(TAG, "数据长度：" + recvBuffLen + " 数据类型:" + recvDataType);
                            if(recvDataType == 2){//如果数据类型为“书籍内容”
//                                timer.start();  //开启定时器锁
                                SendSocketCmdBroadcast(dataType_bookSize, Integer.toString(recvBuffLen));
                            }
                            OnePercentProgress = recvBuffLen / 100;
                            if(recvBuffLen > MAX_RECVBUFF_LEN){
                                Log.e(TAG, "此帧数据超出接收能力");
                                recvBuffIndex = 0;
                                continue;
                            }
                            isStartRecvData = true;
                        }else{
                            continue;
                        }
                    }

                    if(isStartRecvData == true){
                        /**
                         * 进度每达到1% 更新一次进度条（只有在接受数据类型为“小说内容”时才更新进度条）
                         */
                        Log.e(TAG, "recvBuffIndex:" + recvBuffIndex + " recvBuffLen:" + recvBuffLen);
                        if(recvDataType == 2 && recvBuffIndex >= (OnePercentProgress * percent)){
                            percent++;
                            SendSocketCmdBroadcast(dataType_downloadProgress, Integer.toString(recvBuffIndex - 14));
//                            if(!timerLock.isLocked()){  //如果没被锁住 才能发送广播 避免发送过快 程序崩溃
//                                Log.e(TAG, "发送广播");
//
//                                try {
//                                    timerLock.lock();
//                                } catch (InterruptedException e) {
//                                    e.printStackTrace();
//                                }
//                            }
                        }
                        if(recvBuffIndex >= recvBuffLen){//接受完毕
                            int currentIndex = currentRecvBuffIndex;
                            //处理粘连在一起的包
                            do {
                                recvDataType = recvBuff[currentIndex + 1] - '0';
                                //数据长度 $1,xxxxxxxxxx,
                                try{
                                    recvBuffLen = Integer.valueOf(new String(recvBuff,currentIndex + 3,10));
                                } catch (NumberFormatException e){
                                    Log.e(TAG, "recvBuffLen Integer.valueOf：" + e);
                                }

                                Log.e(TAG, "len:" + recvBuffLen + " dataType:" + recvDataType);
                                if(recvDataType == 2){
                                    Log.e(TAG, "currentIndex + 14:" + (currentIndex + 14));
                                    System.arraycopy(recvBuff, currentIndex + 14, Buff.buff,0, recvBuffLen-14);
//                                     = new String(recvBuff,currentIndex + 14,recvBuffLen-14);
                                    Buff.buffByteSize = recvBuffLen-14;
                                    SendSocketCmdBroadcast(recvDataType,"bookContent");
                                }else{
                                    SendSocketCmdBroadcast(recvDataType,new String(recvBuff,currentIndex + 14,recvBuffLen-14));
                                }

                                currentIndex += recvBuffLen;
                            }while(currentIndex < recvBuffIndex);
                            isStartRecvData = false;
                            recvBuffIndex = 0;
                        }
                    }


                } catch (IOException e) {
                    Log.e(TAG, "IOException");
                    e.printStackTrace();
                    break;
                }
            }
        }
    }

    private void SendSocketCmdBroadcast(int dataType, String data){
        Intent intent = new Intent(SOCKET_CMD_RECV);
        intent.putExtra("dataType",dataType);
        intent.putExtra("data",data);
        sendBroadcast(intent);
    }

    private void SendSocketInfoBroadcast(int infoType, String data){
        Intent intent = new Intent(SOCKET_INFO);
        intent.putExtra("infoType",infoType);
        intent.putExtra("data",data);
        sendBroadcast(intent);
    }


    //通过发送数据
    //连接服务器
    public class SocketSendData extends Thread{
        @Override
        public void run() {
            while(true){
                if(isStartSendData == true){
                    isStartSendData = false;
                    Log.e(TAG, "发送数据");
                    try {
                        outputStream.write(sendBuff);
                    } catch (IOException e) {
                        Log.e(TAG, "发送失败");
                        e.printStackTrace();
                    }
                }
            }
        }
    }



    public class SocketBroadcastRecv extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            //在这里写上相关的处理代码，一般来说，不要此添加过多的逻辑或者是进行任何的耗时操作
            //因为广播接收器中是不允许开启多线程的，过久的操作就会出现报错
            //因此广播接收器更多的是扮演一种打开程序其他组件的角色，比如创建一条状态栏通知，或者启动某个服务
            Log.e(TAG, "SocketBroadcastRecv - onReceive: ");
            if(intent.getAction().equals(SOCKET_CMD_SEND)){
                String data = intent.getStringExtra("data");
                Log.e(TAG, "onReceive: data:" + data );
                try {
                    sendBuff = data.getBytes("gbk");
                } catch (UnsupportedEncodingException e) {
                    e.printStackTrace();
                }
                isStartSendData = true;
//                SocketSendData(data);
            }

        }
    }

    //注册广播 与其他组件进行通信
    public void SocketRegisterReceiver(){
        IntentFilter intentFilter = new IntentFilter();
        intentFilter.addAction(SOCKET_CMD_SEND);
        //注册发送数据广播
        registerReceiver(socketBroadcastRecv,intentFilter);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.e(TAG, "onStartCommand: ");
        SocketRegisterReceiver();
        new ConnectServerThread().start();
        return super.onStartCommand(intent, flags, startId);
    }

    public SocketService() {
    }

    @Override
    public void onDestroy() {
        unregisterReceiver(socketBroadcastRecv);
        super.onDestroy();
    }
}
