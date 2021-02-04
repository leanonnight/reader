package com.example.reader.BookItem;

public class BookData {
    private String title;   //项标题
    private String inline_block;    //作者 更新时间
    private String theLasterChapter;    //最后更新章节

    public void setTitle(String title){
        this.title = "title: " + title;
    }

    public void setInlineBlock(String inline_block){
        this.inline_block = "inline: " + inline_block;
    }

    public void setTheLasterChaoter(String theLasterChapter){
        this.theLasterChapter = "new_chapter: " + theLasterChapter;
    }

    public String getTitle(){
        return title;
    }

    public String getInline_block(){
        return inline_block;
    }

    public String getTheLasterChapter(){
        return theLasterChapter;
    }

}
