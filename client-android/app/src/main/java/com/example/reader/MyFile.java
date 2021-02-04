package com.example.reader;

import android.content.Context;
import android.os.Environment;
import android.util.Log;

import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import java.util.zip.Inflater;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class MyFile {
    private static String TAG = "reader-MyFile";
    private static Context context;

    public MyFile(Context context) { //通过构造方法传入context
        this.context = context;
    }

    public MyFile() {

    }

    //保存文件
    public void saveFileToDataArea(String filename, String content) throws Exception { //异常交给调用处处理
        FileOutputStream out = context.openFileOutput(filename, Context.MODE_PRIVATE);
        out.write(content.getBytes());
        out.close();
    }

    public String readFileFromDataArea(String filename) throws Exception { //异常交给调用处处理
        FileInputStream in = context.openFileInput(filename);
        byte b[] = new byte[1024];
        int len = 0;
        ByteArrayOutputStream array = new ByteArrayOutputStream();
        while ((len = in.read(b)) != -1) { //开始读取文件
            array.write(b, 0, len);
        }
        byte data[] = array.toByteArray(); //把内存里的数据读取出来
        in.close(); //每个流都必须关闭
        array.close();
        return new String(data); //把byte数组转换为字符串并返回
    }

    /**
     * 外部存储的状态
     *
     * @return
     */
    public static boolean isExternalStorageWritable() {
        String state = Environment.getExternalStorageState();
        if (Environment.MEDIA_MOUNTED.equals(state)) {
            return true;
        }
        Log.e("state=", "" + state);
        return false;
    }

    public String saveFileToSDcard(String filename, byte[] data) {
        if (!isExternalStorageWritable()) {
            return null;
        }

        File dir = context.getExternalFilesDir("book");
        Log.e(TAG, "writeStringToFile: dir = " + dir.getAbsolutePath());

        if (!dir.exists()) {
            dir.mkdirs();
        }

        File file = new File(dir, filename);
        if (file.exists()) {
            file.delete();
        }

        FileOutputStream fos = null;
        BufferedOutputStream bos = null;
        try {
            file.createNewFile();

            fos = new FileOutputStream(file);
            bos = new BufferedOutputStream(fos);
            bos.write(data);
            bos.close();
            fos.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (bos != null) {
                    bos.close();
                }
                if (fos != null) {
                    fos.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return file.getAbsolutePath();
    }

    /**
     * zip解压
     *
     * @param srcFile     zip源文件
     * @param destDirPath 解压后的目标文件夹
     * @throws RuntimeException 解压失败会抛出运行时异常
     */

    public static void unZip(File srcFile, String destDirPath) throws RuntimeException {

        long start = System.currentTimeMillis();

        // 判断源文件是否存在

        if (!srcFile.exists()) {

            throw new RuntimeException(srcFile.getPath() + "所指文件不存在");

        }

        // 开始解压

        ZipFile zipFile = null;

        try {

            zipFile = new ZipFile(srcFile);

            Enumeration<?> entries = zipFile.entries();

            while (entries.hasMoreElements()) {

                ZipEntry entry = (ZipEntry) entries.nextElement();

                System.out.println("解压" + entry.getName());

                // 如果是文件夹，就创建个文件夹

                if (entry.isDirectory()) {

                    String dirPath = destDirPath + "/" + entry.getName();

                    File dir = new File(dirPath);

                    dir.mkdirs();

                } else {

                    // 如果是文件，就先创建一个文件，然后用io流把内容copy过去

                    File targetFile = new File(destDirPath + "/" + entry.getName());

                    // 保证这个文件的父文件夹必须要存在

                    if (!targetFile.getParentFile().exists()) {

                        targetFile.getParentFile().mkdirs();

                    }

                    targetFile.createNewFile();

                    // 将压缩文件内容写入到这个文件中

                    InputStream is = zipFile.getInputStream(entry);

                    FileOutputStream fos = new FileOutputStream(targetFile);

                    int len;

                    byte[] buf = new byte[100000000];

                    while ((len = is.read(buf)) != -1) {

                        fos.write(buf, 0, len);

                    }

                    // 关流顺序，先打开的后关闭

                    fos.close();

                    is.close();

                }

            }

            long end = System.currentTimeMillis();

            System.out.println("解压完成，耗时：" + (end - start) + " ms");

        } catch (Exception e) {

            throw new RuntimeException("unzip error from ZipUtils", e);

        } finally {

            if (zipFile != null) {

                try {

                    zipFile.close();

                } catch (IOException e) {

                    e.printStackTrace();

                }

            }

        }
    }



    /**
     * 解压缩
     *
     * @param data
     *            压缩的数据
     * @return byte[] 解压缩后的数据
     */
    public static byte[] decompress(byte[] data) {
        Log.e(TAG, "decompress:开始");
        //定义byte数组用来放置解压后的数据
        byte[] output = new byte[0];
        Inflater decompresser = new Inflater();
        decompresser.reset();
        //设置当前输入解压
        Log.e(TAG, "decompress:data.length");
        decompresser.setInput(data, 0, data.length);
        ByteArrayOutputStream o = new ByteArrayOutputStream(data.length);
        try {
            byte[] buf = new byte[1024];
            while (!decompresser.finished()) {
                Log.e(TAG, "decompress:run");
                int i = decompresser.inflate(buf);
                o.write(buf, 0, i);
            }
            output = o.toByteArray();
        } catch (Exception e) {
            output = data;
            e.printStackTrace();
        } finally {
            try {
                o.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        decompresser.end();
        Log.e(TAG, "decompress:结束");
        return output;
    }


}
