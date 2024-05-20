# MCTP

## Endpoint ID assignment and endpoint ID pools

Bus owners are MCTP devices that are responsible for issuing EIDs to devices on a bus segment. 
These EIDs come from a pool of EIDs maintained by the bus owner.

With the exception of the topmost bus owner (see 8.17.1), a given bus owner’s pool of EIDs is
dynamically allocated at run-time by the bus owner of the bus above it in the hierarchy.

## Use of static EIDs and static EID pools

In general, the only device that will require a static (pre-configured default assigned non-zero value) EID
assignment will be the topmost bus owner.

If the device functions as an MCTP bridge, it will require `a static pool of EIDs` to be assigned
to it as part of the system design.

## Endpoint ID retention
Devices should retain their EID assignments for as long as they are in their normal operating state.
Asynchronous conditions, such as device errors, unexpected power loss, power state changes, resets,
firmware updates, may cause a device to require a reassignment of its EID

- Endpoint
  - 配置的 EID 來自 `Bus owner` 或是 `Top Bus`
  - 取得 EID 配置後, 會儲存 Bus Owner 資訊 (目前得知 : Physical Address)
  - 不需要知道其他 `Endpoint Address` 位址, 只要知道 `Bus Owner Address`

- Bridge      
    - Bridge would announce the need for EID assignment for the interface
    - Bridge can accept an EID assignment for each bus independently
    - Bridge’s configuration functionality may be accessed through multiple EIDs.
    - Bus Owner or top buse owner assigne EIDs pool to bridge (Using Allocate Endpoint IDs Commad)
    - Bridge has only one EID Pool

- Question:    
    - Bridge 只接受到 EID Pool Allocation, 但是並沒有說是來自 `static pool of EIDS`    
