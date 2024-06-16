# Cold Reset

主電源 ( Main Power ) 開啟或是重啟電源 ( Power Cycle )，都會導致 Cold Reset。

例如 :  Intel IO 控制器中心 (ICH) 晶片可以根據系統電源的狀態產生 PERST# 訊號，這表示主電源已打開且穩定。如果電源關閉會造成 PERST# Assert and Dessert 然而導致 Cold Reset。
# Warm Reset

不用移除裝置或是主電源 ( 保持電源不變 )，例如 : 改變系統的電源管理狀態，可能會觸發 Warm Reset。 
但是 PCIe 協議並沒有規範相關定義。