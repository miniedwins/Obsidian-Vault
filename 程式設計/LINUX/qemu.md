## 編譯 QEMU 原始碼

github 下載原始碼

```
$ git clone https://github.com/qemu/qemu.git
$ cd qemu
$ git checkout v8.2.0
```

參數說明 :
- targret-list : 選擇目標機器的架構。(Default : 所有的架構都編譯)
- enable-debug : 編譯時，將所有的警告當作錯誤處理。
- enable-kvm : 編譯KVM模組，使QEMU可以利用KVM來訪問硬體提供的虛擬化服務。

```
$ ./configure --target-list=arm-softmmu,x86_64-softmmu,aarch64-softmmu \ 
--enable-debug --enable-kvm

$ make
$ make install
```
