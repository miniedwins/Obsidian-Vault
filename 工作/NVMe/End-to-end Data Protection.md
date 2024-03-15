## Metadata 
- 主要存放的是 `Protection Information (PI)`
- 傳輸方式分為兩種 
  - DIF :
  - DIX :    

## PI

組成結構內容 
- Guard
- Application Tag
- Reference Tag

## Guard Protection 

`Guard Filed` 存放計算 `Logic Block Data` 後的 `CRC` ，不過會因為 `PI` 的位置在
Metadata 前面 (First bytes) 或是後面 (Last Bytes) 會有所不同，條件如下 :

Metadata Size > PI Size
- PI 位置在 Meadata 前面 (First bytes)
  - CRC = Logic Block Data
- PI 位置在 Meadata 後面 (last bytes)
  - CRC = Logic Block Data + Metadata (Excluding PI)



