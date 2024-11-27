
### **1. Class Code Register Format**

The Class Code register is 3 bytes (24 bits) wide and structured as follows:

|**Offset**|**Bits**|**Field**|**Description**|
|---|---|---|---|
|`0x09`|8 (23:16)|Base Class Code|General category of the device (e.g., storage, network).|
|`0x0A`|8 (15:08)|Subclass Code|Specific functionality within the Base Class Code.|
|`0x0B`|8 (07:00)|Programming IF|(Optional) Programming interface of the device.|

---

### **2. Base Class Codes and Subclass Codes**

#### **Common Base Class Codes**

|**Base Class Code**|**Description**|
|---|---|
|`00`|Unclassified|
|`01`|Mass Storage Controller|
|`02`|Network Controller|
|`03`|Display Controller|
|`04`|Multimedia Controller|
|`05`|Memory Controller|
|`06`|Bridge Device|
|`07`|Simple Communication Controller|
|`08`|Base System Peripheral|
|`09`|Input Device Controller|
|`0A`|Docking Station|
|`0B`|Processor|
|`0C`|Serial Bus Controller|
|`0D`|Wireless Controller|
|`0E`|Intelligent Controller|
|`0F`|Satellite Communication Controller|
|`10`|Encryption/Decryption Controller|
|`11`|Data Acquisition and Signal Processing Controller|
|`FF`|Undefined Device|

---

#### **Example Subclass Codes for Base Class Code `01` (Mass Storage Controller)**

|**Subclass Code**|**Description**|
|---|---|
|`00`|SCSI Bus Controller|
|`01`|IDE Controller|
|`02`|Floppy Disk Controller|
|`03`|IPI Bus Controller|
|`04`|RAID Controller|
|`05`|ATA Controller|
|`06`|SATA Controller|
|`07`|SAS Controller|
|`08`|NVM Controller (e.g., NVMe)|
|`80`|Other Mass Storage Controller|

---

### **3. Programming Interface Field**

- Some devices include a **Programming Interface** field to further define their functionality.
- **Example for Base Class Code `01`, Subclass Code `06` (SATA Controller)**:
    - `00`: Vendor Specific Interface.
    - `01`: AHCI 1.0 Interface.

---

### **4. How to Check Base and Subclass Codes**

You can use `lspci` to inspect these fields on a Linux system:

bash

複製程式碼

`lspci -nn`

Example output:

plaintext

複製程式碼

`01:00.0 Non-Volatile memory controller [0108]: Samsung Electronics Co Ltd NVMe SSD Controller [144d:a802]`

- **Class Code `[0108]`**:
    - Base Class Code: `01` (Mass Storage Controller).
    - Subclass Code: `08` (NVM Controller).