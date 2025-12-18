## Test Steps

### Step 1: Assign Namespace Global Ranges

1. Assign Global Range to NS1
   - NSID = 1
   - RangeStart = 0
   - RangeLength = 0   (entire namespace)

2. Assign Global Range to NS2
   - NSID = 2
   - RangeStart = 0
   - RangeLength = 0

3. Assign Global Range to NS3
   - NSID = 3
   - RangeStart = 0
   - RangeLength = 0

### Step 2: Assign Namespace Non-Global Ranges

4. Assign a Non-Global Range to NS1
   - NSID = 1
   - RangeStart = 0
   - RangeLength = 64

5. Assign a Non-Global Range to NS2
   - NSID = 2
   - RangeStart = 64
   - RangeLength = 128

6. Assign a Non-Global Range to NS3
   - NSID = 3
   - RangeStart = 128
   - RangeLength = 256


## Steps

1. Ensure three namespaces exist and are attached:
   - NS1 (NSID = 1)
   - NS2 (NSID = 2)
   - NS3 (NSID = 3)

2. Ensure each namespace has a Namespace Global Range assigned
   covering the entire namespace.

3. Ensure each namespace has one Namespace Non-Global Locking Range configured:
   - NS1: RangeStart = 0,   RangeLength = 64
   - NS2: RangeStart = 64,  RangeLength = 128
   - NS3: RangeStart = 128, RangeLength = 256

4. Ensure all Global and Non-Global Locking Ranges are in a fully unlocked state.


## Validation

- Query the Locking Table and confirm:
  - One Global Range and one Non-Global Range exist per namespace.
  - RangeStart and RangeLength match the expected values.
- Confirm no read or write locks are enabled.

======================================================
# Precondition: Namespace Non-Global Ranges Configured

## Description

This precondition defines a system state where multiple namespaces
already have Namespace Non-Global Locking Ranges configured
with different LBA ranges.
All locking ranges are unlocked.

## Depends On

- Precondition: opal_initialized_unlocked

## Steps

1. Ensure the following namespaces exist and are attached:
   - NS1
   - NS2
   - NS3

2. Ensure each namespace has a Namespace Non-Global Locking Range configured
   with the following parameters:
   - NS1: RangeStart = 0,   RangeLength = 64
   - NS2: RangeStart = 64,  RangeLength = 128
   - NS3: RangeStart = 128, RangeLength = 256

3. Ensure all Namespace Non-Global Locking Ranges are in a fully unlocked state.