首先安裝編譯所需要的套件

```shell
$ sudo apt-get install gcc make meson libglib2.0-dev python3-venv
```

下載 QEMU 原始碼

```
$ git clone https://github.com/qemu/qemu.git
$ cd qemu
$ git checkout v8.2.0
```

 - 環境配置 
	- targret-list : 選擇目標機器的架構。(Default : 所有的架構都編譯)
	- enable-debug : 將所有的警告當作錯誤處理。
	- enable-kvm : 使QEMU可以利用KVM來訪問硬體提供的虛擬化服務。

```
$ ./configure --target-list=arm-softmmu,x86_64-softmmu,aarch64-softmmu \ 
--enable-debug --enable-kvm
```

編譯套件 & 安裝套件

```
$ make
$ make install
```