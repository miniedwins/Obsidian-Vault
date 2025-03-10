# 自動電源狀態切換 (APST)
**Autonomous Power State Transitions (APST) :** 提供主機一個電源狀態自動切換的機制，能讓主機可以切換電源階段 (a non-operational power state may autonomously transition to another non-operational power state)。它的進入的條件是當控制器連續閒置 (Idle) 一段時間，並且超過所指定的閒置時間，主機就會轉換電源狀態到 NOPS。

注意 : 如果電源階段是在 **Non-Operational States (NOPS)**，這個時候控制器可能會去運行像是 **Device Self-Test (DST)** 操作，那就可能會超過控制器所宣告該電源階段的最大功耗值 (MP)，此時控制器不應該切換到 NOPS。

*備註 : Controller idle means that there are no commands outstanding to any I/O Submission Queue*
