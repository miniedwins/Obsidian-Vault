# MCTP

## Endpoint ID assignment and endpoint ID pools

Bus owners are MCTP devices that are responsible for issuing EIDs to devices on a bus segment. 
These EIDs come from a pool of EIDs maintained by the bus owner.

With the exception of the topmost bus owner (see 8.17.1), a given bus owner’s pool of EIDs is
dynamically allocated at run-time by the bus owner of the bus above it in the hierarchy.



