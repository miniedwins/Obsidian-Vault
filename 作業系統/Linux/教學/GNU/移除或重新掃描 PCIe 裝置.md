說明：某個情況下可能需要先將裝置移除，然後再重新掃描所有的 PCIe，讓系統去初始化剛剛移除裝置。

備註：需要切換 `ROOT` 帳號

```
# 移除指定的 PCIe 裝置　
$ echo 1 > /sys/bus/pci/devices/0000\:01\:00.0/remove

# 重新掃描所有 PCIe 裝置
$ echo 1 > /sys/bus/pci/devices/0000\:00\:00.0/rescan
```