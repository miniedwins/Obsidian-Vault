
- 測試目的 :  驗證 MaxSubPackets + 1 ( 當前 TPer MaxSubPackets=1)
- 期望結果 :  回傳 no further data
- 測試說明 : 
	- Host 調用 Properties Method，取得 MaxSubPackets 
	- 主機發送多個 MaxSubPackets + 1
		- ComPacket = Packet + Subpacket 1 + Subpacket 2
	- 確認回傳結果狀態






