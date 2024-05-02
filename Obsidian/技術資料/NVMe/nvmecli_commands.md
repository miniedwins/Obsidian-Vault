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

## Read VPD
nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x05 -m 1 -0 0 -1 0x100 -l 256

## Write VPD
