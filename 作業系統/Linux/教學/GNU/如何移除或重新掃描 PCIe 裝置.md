
說明：某個情況下可能需要先將裝置移除後，再重新在掃描一次整個讓系統去重置剛剛移除的裝置

移除指定的 PCIe 裝置

```
$ echo 1 > /sys/bus/pci/devices/0000\:01\:00.0/remove
```

重新掃描所有 PCIe 裝置

```
$ echo 1 > /sys/bus/pci/devices/0000\:00\:00.0/rescan
```

