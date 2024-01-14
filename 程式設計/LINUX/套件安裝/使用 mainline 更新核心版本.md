## 安裝套件

安裝 mainline 套件

```
# 首先加入新的倉庫到系統中
$ sudo add-apt-repository ppa:cappelikan/ppa

# 更新套件清單
$ sudo apt-get update

# 安裝 mainline
$ sudo apt install mainline
```

列出可用的更新版本

```
$ mainline --list

mainline 1.0.15
Distribution: Ubuntu 20.04.3 LTS
Architecture: amd64
Running kernel: 5.10.60-051060-generic
Fetching index from kernel.ubuntu.com...
OK
----------------------------------------------------------------------
Found installed: 5.10.60-051060.202108180439
Found installed: 5.13.0-28.31~20.04.1
Found installed: 5.13.0-30.33~20.04.1
Found installed: 5.13.0-27.29~20.04.1
Found installed: 5.13.0.30.33~20.04.17
----------------------------------------------------------------------
----------------------------------------------------------------------

======================================================================
Available Kernels
======================================================================
5.16.10                          
5.16.9                           
..... (略過)                  
5.0.5                            
5.0.0 
```

基本上可以使用兩種方法更新，安裝完成後，會自動執行開機選單更新。

- 方法 (1) : 直接更新到最新的版本
	- `mainline --install-latest`
- 方法 (2) : 指定特定版本更新
	- `mainline --install 5.10.60`

## 移除套件

列出已安裝的清單

```
$ mainline --list-installed 

mainline 1.0.15
Distribution: Ubuntu 20.04.3 LTS
Architecture: amd64
Running kernel: 5.10.60-051060-generic
----------------------------------------------------------------------
Found installed: 5.10.60-051060.202108180439
Found installed: 5.13.0-28.31~20.04.1
Found installed: 5.13.0-30.33~20.04.1
Found installed: 5.13.0-27.29~20.04.1
Found installed: 5.13.0.30.33~20.04.17
----------------------------------------------------------------------
----------------------------------------------------------------------
```

選擇移除核心版本，可以移除舊版本或是指定版本移除

```
# 移除舊版本
$ mainline --uninstall-old

# 指定移除核心版本
$ mainline --uninstall 5.10.60
```

最後清除快取檔案

```
$ mainline --clean-cache
```

輸出結果 :

```
mainline 1.0.15
Distribution: Ubuntu 20.04.3 LTS
Architecture: amd64
Running kernel: 5.13.0-30-generic
```