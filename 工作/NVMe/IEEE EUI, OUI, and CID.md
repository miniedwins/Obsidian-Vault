# IEEE EUI, OUI, and CID

> IEEE - Guidelines for Use of EUI, OUI, and CID  
> [https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/tutorials/eui.pdf](https://standards.ieee.org/content/dam/ieee-standards/standards/web/documents/tutorials/eui.pdf)

IEEE註冊機構(IEEE RA)分配以下標識符:

- 組織唯一標識符(Organizationally Unique Identifierc OUI)
- 公司標識符 (Company ID, CID)
- 擴展唯一標識符 (Extended Unique Identifier, EUI)
- 擴展本地標識符 (Extended Local Identifier, ELI)

## OUI and CID

**OUI**與**CID**皆為24位元(3個位元組)的標識符，它們來自相同的24位元空間但屬於不同的子空間，由一個稱為`X`位元的特定位元區分。每個被分配的OUI和CID對於所有分配的OUI和CID1是唯一的。

|X bit|identifier|
|---|---|
|0|OUI|
|1|CID|

**OUI**或**CID**可用於識別公司，組織，實體，製造商，供應商等。36位元OUI-36作為組織的全球唯一標識符。**OUI-36**的前24位元不會重複分配。

### OUI

**OUI**是24位元(3個位元組)序列：

- Octet 0是初始(最高有效)的位元組。其最小和第二最低有效位元分別指定為`M`位元和`X`位元。在**OUI**中，`M`和`X`位元都具有值0。

Octet 0Octet 1Octet 27654321X bit `0`0M bit `0`

- **OUI**可以表示為6個16進制數字(base-16)

Octet idHexBinary0AC101011001DE1101111024801001000MSBLSB

### OUI-36

**OUI-36**是一個36位元(4個位元組+半個位元組)序列：

- Octet 0是初始(最高有效)的位元組。其最小和第二最低有效位元分別指定為`M`位元和`X`位元。在**OUI-36**中，`M`和`X`位元都具有值0。
- **OUI**的受讓人可以通過在被分配的OUI的末尾新增12位來創建**OUI-36**。如果**OUI-36**的受讓人需要唯一的24位組織標識符，則建議使用**CID**分配。
- **OUI-36**可以表示為9個16進制數字(base-16)

Octet idHexBinary0AC101011001DE110111102480100100032300100011440100MSBLSB

- IEEE RA通過將12位元連接到24位元IEEE保留基底**OUI**(IEEE-reserved base OUI)來創建**OUI-36**，在Octet 2的最低有效位之後連接這12位元。
- 基底**OUI**不會分配給另一個組織或以其他方式用作**OUI**。
- **OUI-36**的受讓人不得截斷**OUI-36**以用作**OUI**，因為IEEE RA將使用 基底**OUI**將**OUI-36**值分配給多個組織。

### CID

**CID**是24位元(3個位元組)序列：

- Octet 0是初始(最高有效)的位元組。從最低有效位元開始，將Octet 0的四個最低有效位元分別指定為`M`位元，`X`位元，`Y`位元和`Z`位元。 在**CID**中，`M`，`X`，`Y`和`Z`位元分別具有值0,1,0和1。

Octet 0Octet 1Octet 276543Z bit `1`2Y bit `0`1X bit `1`0M bit `0`

- **CID**可以表示為6個16進制數字(base-16)

Octet idHexBinary0AA101010101DE1101111024801001000MSBLSB

## 擴展標識符

除了用作全域唯一組織標識符之外，**OUI**，**OUI-36**或**CID**可以通過串聯附加的區分位元來作為擴展標識符的基礎，包括協議標識符和上下文相關標識符。這些擴展標識符可以是全域唯一的(例如，**EUI-48**和**EUI-64**)，或者僅在它們被使用的上下文中是唯一的。

### EUI

- 擴展唯一標識符 (Extended Unique Identifier, EUI)是48位元(**EUI-48**)或64位元(**EUI-64**)。
- 除了一些例外，特別是在協議標識符方面，每個EUI旨在全域唯一併綁定到硬體設備實例或需要唯一標識的其他對象。
- **EUI-48**和**EUI-64**標識符最常用作全球唯一的網路位址(有時稱為MAC位址)，如各種標準中所規定：
    - **EUI-48**通常用作根據IEEE Std 802的硬體介面位址(MAC-48)。
    - **EUI-64**可以用作IEEE Std 1588的時鐘標識符。
    - IEEE Std 802還指定**EUI-64**用於64位元全域唯一網路位址
- 當**EUI**用作MAC位址，初始位元組(Octet 0)的兩個最低有效位元用於特殊目的。
    - Octet 0的最低有效位元(`I/G`位元)表示獨立位址(`I/G=0`)或群組位址(`I/G=1`)
    - Octet 0的第二個最低有效位元(`U/L`位元)表示位址的通用管理(`U/L=0`)或本地管理(`U/L=1`)。
    - 被通用管理的位址旨在成為全球唯一的位址。
- 在通過擴展**OUI**創建的**EUI**中，**OUI**是初始(最高有效)的3個位元組。
- 在通過擴展**OUI-36**創建的**EUI**中，**OUI-36**初始(最高有效)的4個半位元組。
- 由於**OUI**和**OUI-36**的`X`位元等於0，因此創建的**EUI**具有`U/L=0`，並且當用作MAC位址時，是一個通用管理位址。
- 由於**OUI**和**OUI-36**的`M`位元等於0，因此創建的**EUI**具有`I/G=0`，並且當用作MAC位址時，是一個獨立位址。
- **OUI**或**OUI-36**的受讓人設置`M`位元為1來分配群組MAC位址(`I/G=1`)。

### ELI

- 擴展本地標識符 (Extended Local Identifier, ELI)是通過來自**CID**的串聯創建的，**CID**是初始(最高有效)的3個位元組**ELI-48**是48位元，**ELI-64**是64位元。
- **CID**的`X`位元等於1，**ELI**具有`U/L=1`，因此當用作MAC地址時，是本地位址。
    - 本地位址不是全域唯一的，網絡管理員負責確保分配的任何本地位址在使用範圍內是唯一的。
    - 從IEEE Std 802c-2017開始，規定了結構化本地位址規劃(Structured Local Address Plan, SLAP)，它描述了**ELI**在一個象限中的使用。
    - 本地MAC位址空間，基於**CID**的`Y`位元和`Z`位元的指定值。
    - 在本地MAC位址空間的其他像限中，SLAP描述了不基於**CID**的標準分配標識符(Standard Assigned Identifier, SAI)和管理分配標識符(Administratively Assigned Identifiers，AAI)。
- **CID**的`M`位元等於0，**ELI**具有`U/L=0`，因此當用作MAC地址時，是獨立位址。
    - **CID**的受讓人可以通過將`M`位元設置為1來分配本地群組MAC地址(`I/G=1`)。

## IEEE RA 標識符的分配

IEEE RA以三種不同的大小分配EUI區塊：

- **MA-L**分配區塊提供224個**EUI-48**標識符和240個**EUI-64**標識符。
    - 用**OUI**為分配基礎
- **MA-M**分配區塊塊提供220個**EUI-48**標識符和236個**EUI-64**標識符。
    - 用**OUI-36**或**CID**為分配基礎
- **MA-S**分配區塊塊提供212個**EUI48**標識符和228個**EUI-64**標識符。
    - 用**OUI-36**為分配基礎
- **CID**是一個唯一的24位元標識符，可用於標識公司，組織等
    - CID不得用於創建**EUI-48**或**EUI-64**。
    - 對於尋求唯一24位元標識符的實體，**CID**可以與**MA-M**或**MA-S**分配互補，因為這些分配不包括**OUI**。

|IEE RA分配|分配位元數|**EUI-48**區塊大小|**EUI-64**區塊大小|包括**OUI**或**CID**|
|---|---|---|---|---|
|MA-L|24|224|240|OUI-24|
|MA-M|28|220|236|none|
|MA-S|26|212|228|OUI-36|
|CID|24|0|0|CID|

### EUI結構與表徵

EUI-48的結構及其與IEEE RA分配的關係。

Octet id012345MA-LOUI-2424-bit extensionMA-M28-bit MA-M base20-bit extensionMA-SOUI-3612-bit extensionHexACDE48234567Binary101011001101111001001000001000110100010101100111

EUI-64的結構及其與IEEE RA分配的關係。

Octet id01234567MA-LOUI-2440-bit extensionMA-M28-bit MA-M base36-bit extensionMA-SOUI-3628-bit extensionHexACDE48234567019FBinary1010110011011110010010000010001101000101011001110000000110011111

### EUI 位元順序

雖然EUI位元組的順序和位元組內的位元是特定的和固定的，但是它們的傳輸順序可以根據協議而變化。通常，基於位元組的傳輸以位元組標識符的升序發送，從位元組0開始。有關位元傳輸順序的更多資訊可在相關標準中獲得，例如IEEE Std 802。  
鑑於位元順序和位元組定位可能混淆，應用程序和協議必須明確指定標識符值(表示為十六進制數字)到適用的暫存器或位元組和位元序列的對應。為確保清晰，每個對應應該是獨立的。

### 未分配和NULL EUI值

許多應用程序發現定義不同的空標識符很有用，通常表明缺少有效的EUI-48或EUI-64值。 例如，空值可能是整合電路暫存器的上電狀態，直到硬體或韌體使用有效的EUI初始化暫存器。 類似地，在將另一設備或對象的EUI放置在協議欄位中的情況下，可以使用空值直到學習要放置在協議欄位中的有效EUI值。 管理資訊庫參數也可能面臨類似的初始值問題，其使用方便的空值。

- 全零EUI-48值(00-00-00-00-00-00)和EUI-64值(00-00-00-00-00-00-00-00)，雖然分配給一個組織， 該受讓人未曾也不會將其用作EUI。(它們可被視為分配給IEEE註冊機構。)
- 全1位48位值(FF-FF-FF-FF-FFFF)和64位值(FF-FF-FF-FF-FF-FF-FF-FF)是指示網絡上所有站的IEEE 802多播(組)MAC地址。這些全值的值不是有效的EUI。
- 建議的空值為全1位值，分別為未知EUI-48和EUI-64值的默認值。
- 全零值不得用作標識符。