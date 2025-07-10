
- With the exception of the last packet in a message, the MCTP Transmission Unit size of all packets in a given message shall be equal to the negotiated MCTP Transmission Unit Size;

- The MCTP Transmission Unit size of the last packet in a Request Message or Response Message (i.e., the one with the EOM bit set in the MCTP header) shall be the smallest size required to transfer the MCTP Packet Payload for that Packet with no additional padding beyond any padding required by the physical medium-specific trailer; and • 

- Once a complete NVMe-MI Message has been assembled, the Message Integrity Check is verified. If the Message Integrity Check passes, then the NVMe-MI Message is processed. If the Message Integrity Check fails, then the NVMe Message is discarded. Refer to section 4.2.