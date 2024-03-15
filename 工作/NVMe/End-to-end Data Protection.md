# End-to-end Data Protection

## Metadata 
- 主要存放的是 `Protection Information (PI)`
- DIF :
- DIX : 

## PI
- Guard Protection
  - PI 放在 Meadata 前面 (First bytes)
    - CRC = Logic Block Data
  - PI 放在 Meadata 後面 (last bytes)
    - CRC = Logic Block Data + Metadata (Excluding PI)
