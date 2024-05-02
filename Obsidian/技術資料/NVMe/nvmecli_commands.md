# Management Interface

## Read VPD
nvme nvme-mi-recv /dev/nvme0n1 --opcode=0x05 -m 1 -0 0 -1 0x100 -l 256

## Write VPD
