## 執行自檢測試
- 選擇自檢類型 : 
	- `0x01` :  Short device self-test 
	- `0x02` :  Extended device self-test

![[Pasted image 20241218033737.png]]

- 指定選擇自檢 NSID 範圍 
	- `0x00000000h` :  
		- 不包括任一個 Namespace。
	- `0x00000001-0xFFFFFFFEh` : 
		- 指定任一個  Active Namespace。
		- 若是指定 Invalid 或是 Inactive NSID，這些無效的命名空間或是未被使用的空間，控制器會中止命令並且回傳 Invalid Field in Command。
	- `0xFFFFFFFFh` : 
		- 所有的 Active Namespaces。

![[Pasted image 20241218033919.png]]

~~~shell
# Short self-test
$ sudo nvme device-self-test /dev/nvme0 --namespace-id=1 --self-test-code=1

# Extended self-test
$ sudo nvme device-self-test /dev/nvme0 --namespace-id=1 --self-test-code=2
~~~

## 停止自檢命令
- 選擇自檢類型 :	 
	- `0xF` : Abort device self-test operation
~~~shell
# Abort the device self-test
$ sudo nvme device-self-test /dev/nvme0 --namespace-id=1 --self-test-code=0xf
~~~

## 查詢 Extended 自檢完成時間
- 發送 `Identify Controller` 命令來取得 `EDSTT` 需要多少時間內完成測試。
- `EDSTT` 結果轉換成 `10` 進制，取得真正的測試時間。
- 如果控制器沒有支援，這個欄位就是保留狀態。

![[Pasted image 20250313100705.png]]

5分鐘完成 Extended Device Self Test。

```shell
$ sudo nvme id-ctrl /dev/nvme0 | grep edstt
# edstt: 5
```


