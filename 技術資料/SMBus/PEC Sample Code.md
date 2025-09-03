
```python
def pec(data):
    """計算 SMBus PEC"""
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc
```

```python
# Reset Device (General)
if __name__ == "__main__": 
	print("SMBus PEC Calculator")
	command = 0x02
	address_with_rw = 0xC2 # 0b11000010
	print(f"PEC = 0x{pec([address_with_rw, command]):02X}") # 0xC9 
```