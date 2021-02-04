package com.example.reader;

public class Buff {
    private static int MAX_RECVBUFF_LEN = 52428800;  //50兆
    public static byte[] buff = new byte[MAX_RECVBUFF_LEN];
    public static int buffByteSize = 0;
}
