
(1) 驗證鏈路狀態

使用以下命令檢查 PCIe 鏈路狀態：

```bash
cat /sys/bus/pci/devices/0000:xx:xx.x/power_state
```

或檢查設備狀態日誌：

```bash
dmesg | grep PCIe
```

(2) 配置 ASPM

在 Linux 中，可以通過以下方式啟用 ASPM：

- **檢查當前策略**：
	- `cat /sys/module/pcie_aspm/parameters/policy`
- **設置策略**：
	- `echo powersave > /sys/module/pcie_aspm/parameters/policy`

**策略選項：**
- **default**：由硬體和操作系統共同決定。
- **powersave**：啟用積極的節能模式。
- **performance**：禁用 ASPM 以提升性能。