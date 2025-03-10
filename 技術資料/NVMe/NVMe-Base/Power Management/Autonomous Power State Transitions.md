Autonomous Power State Transitions（APST）是 NVMe 提供的一種 **自動省電機制**，主要目的是當 SSD 閒置一段時間後，自動降低功耗，提高能源效率。如果 SSD 持續閒置超過「設定的閒置時間」，它會自動進入較低的電源狀態（[[Non-Operational Power States]], NOPS）

如果電源階段是在 `NOPS`，這個時候控制器可能會去運行像是 [[Device Self Test]]（DST）操作，那就可能會超過控制器所宣告該電源階段的最大功耗值（MP），此時控制器不應該切換到較低的電源狀態。

*備註 : Controller idle means that there are no commands outstanding to any I/O Submission Queue*