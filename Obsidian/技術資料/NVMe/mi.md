# Management Interface

## nvme-mi-recv
```
  [  --opcode=<NUM>, -O <NUM> ]         --- opcode (required)
  [  --namespace-id=<NUM>, -n <NUM> ]   --- desired namespace
  [  --data-len=<NUM>, -l <NUM> ]       --- data I/O length (bytes)
  [  --nmimt=<NUM>, -m <NUM> ]          --- nvme-mi message type
  [  --nmd0=<NUM>, -0 <NUM> ]           --- nvme management dword 0 value
  [  --nmd1=<NUM>, -1 <NUM> ]           --- nvme management dword 1 value  
```

## Read NVMe-MI Data Structure

- Uses NVMe Management Dword : 0, 1
- Response Data : Data Structure Type (DTYP)
- Data Structure Type (DTYP)
  - 00 : NVM Subsystem Information
  - 01 : Port Information
  - 02 : Controller List
  - 03 : Controller Information
  - 04 : Optionally Supported Command List
  - 05 : Management Endpoint Buffer Command Support List

### NVM Subsystem Information (DTYP=0x00)

```
$ nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x00 -nmimt=0x01 --nmd0=0x0000001 --nmd1=0x00 --data-len=32
NVMe-MI Receive Command is Success and result: 0x00002000 (status: 0x00, response: 0x000020)
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 01 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

### Port Information (DTYP=0x01)

```
$ nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x00 -nmimt=0x01 --nmd0=0x1000000 --nmd1=0x00 --data-len=32
NVMe-MI Receive Command is Success and result: 0x00002000 (status: 0x00, response: 0x000020)
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 01 00 40 00 00 00 00 00 01 0f 03 04 04 00 00 00 "..@............."
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

### Controller List (DTYP=0x02)

Refer Controller List Format from NVM Express Base Specification

- Controller List Format
  - 01:00 Number of Identifiers
  - 03:02 Identifier 0
  - 05:04 Identifier 1
  - (N*2+3):(N*2+2) Identifier N

We get total numbers IDs and one CTRLID.

```
$ nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x00 -nmimt=0x01 --nmd0=0x2000001 --nmd1=0x00 --data-len=32
NVMe-MI Receive Command is Success and result: 0x00000400 (status: 0x00, response: 0x000004)
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

### Controller Information (DTYP=0x03)

```
$ nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x00 -nmimt=0x01 --nmd0=0x3000001 --nmd1=0x00 --data-len=32
NVMe-MI Receive Command is Success and result: 0x00002000 (status: 0x00, response: 0x000020)
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 00 00 00 00 00 01 00 02 cd 1b 90 01 cd 1b 90 01 "................"
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```

## Read VPD

- Uses NVMe Management Dword : 0, 1
- Response Data : VPD Elements
- Data Length : 256 ~ 4096 Bytes

// TODO : Capature VPD Elements (PAGE: 128)

```
$ nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x05 -nmimt=0x01 1 --nmd0=0x0 --nmd1= 0x100 --data-len=256
NVMe-MI Receive Command is Success and result: 0x00000000 (status: 0x00, response: 0x000000)
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 01 00 00 00 01 0f 00 ef 01 0e 19 c8 50 68 69 73 "............Phis"
0010: 6f 6e 20 20 d8 50 68 69 73 6f 6e 20 20 20 20 20 "on...Phison....."
0020: 20 20 20 20 20 20 20 20 20 20 20 20 20 e8 37 36 "..............76"
0030: 38 30 47 42 20 50 43 49 65 20 44 72 69 76 65 20 "80GB.PCIe.Drive."
0040: 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 "................"
0050: 20 20 20 20 20 20 c2 30 20 d4 38 33 32 34 30 31 ".......0..832401"
0060: 32 30 31 30 31 39 20 20 20 20 20 20 20 20 00 00 "201019.........."
0070: 00 c1 00 00 00 00 00 2f 0b 02 3b 67 51 00 13 00 "......./..;gQ..."
0080: 00 00 00 00 00 00 00 0a 0a 00 64 00 00 00 00 0a "..........d....."
0090: 00 60 25 7d fc 06 00 00 00 00 00 00 00 00 00 00 ".`%}............"
00a0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
00b0: 00 00 00 00 00 00 00 00 0c 02 0b e9 fe 01 00 01 "................"
00c0: 0f 04 01 01 00 00 00 00 0d 82 0f 94 ce 00 00 01 "................"
00d0: 07 00 0c 3b 02 01 00 06 0f 04 01 00 ff ff ff ff "...;............"
00e0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff "................"
00f0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff "................"
```

## Write VPD

// TODO

## NVM Subsystem Health Status Poll

- Uses NVMe Management Dword: 1
- Response Data: NVM Subsystem Health Data Structure (NSHDS)
- Data Length: 8byes

```
$ nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x01 -nmimt=0x01 --nmd0=0x00 --data-len=32
NVMe-MI Receive Command is Success and result: 0x00000000 (status: 0x00, response: 0x000000)
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
0000: 38 ff 32 00 21 03 00 00 00 00 00 00 00 00 00 00 "8.2.!..........."
0010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "................"
```
