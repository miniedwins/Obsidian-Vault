
- Remove PCIe Device

```
echo 1 > /sys/bus/pci/devices/0000\:01\:00.0/remove
```

- Rescan All  PCIe Devices

```
echo 1 > /sys/bus/pci/devices/0000\:00\:00.0/rescan
```