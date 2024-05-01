# PCIe Linux Command

## How to remove pcie devices
```
echo 1 > /sys/bus/pci/devices/0000\:01\:00.0/remove
```
##  Rescan all pcie devices
```
echo 1 > /sys/bus/pci/devices/0000\:00\:00.0/rescan
```
