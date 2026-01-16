

## Sanitized Unexpected Deallocate

請注意這兩個關鍵條件的衝突：

- **條件 (a) 的前半段：** "...for which **No-Deallocate After Sanitize was requested**..."
    
    - **翻譯：** 主機當初下指令時，明明跪求控制器 **「拜託不要 Deallocate (NDAS=1)」**。
        
- **條件 (a) 的後半段：** "...completed successfully **with deallocation of all media**..."
    
    - **翻譯：** 結果控制器執行完畢時，卻 **「執行了 Deallocate」**。
        

**結論：** 你要求「不要刪」(No-Deallocate)，我卻「刪掉了」(With Deallocation)。 對主機來說，這個 Deallocation 的動作是 **「非預期 (Unexpected)」** 的，因為我明明叫你別做的。
