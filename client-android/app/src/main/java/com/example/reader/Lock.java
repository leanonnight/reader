package com.example.reader;

public class Lock{
    private boolean isLocked = false;
    public synchronized void lock() throws InterruptedException{
        while(isLocked){
            wait();
        }
        isLocked = true;
    }

    public boolean isLocked() {
        return isLocked;
    }

    public synchronized void unlock(){
        isLocked = false;
        notify();
    }
}
