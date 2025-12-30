# CNL - NVMe & TCG Opal Test Suite

  

## Project Overview

  

This project contains a comprehensive test suite designed to validate the **TCG Opal Security** compliance of NVMe Solid State Drives (SSDs). The primary goal is to verify security features and ensure that standard NVMe operations adhere to Opal security states and constraints.

  

### Key Testing Areas

  

The testing scope is strictly focused on **Configurable Locking for NVMe Namespaces**:

  

**Core Security Features**:

    - **Locking Ranges**: Validation of Read/Write locking behaviors (`LockingSet`) and global vs. non-global range configurations.

    - **Range Management**: Assignment and deassignment of locking ranges (`Assign`/`Deassign`).

    - **Authentication**: Key generation (`GenKey`) and authority management.

    - **Lifecycle**: Reverting the Security Provider (`Revert`) and Shadow MBR control (`MBRControl`).

  

**Opal Interactions with NVMe Commands**:

    - **Namespace Management** (`Mgmt`): Behavior of Create, Delete, Attach, and Detach commands when Opal is active.

    - **Format NVM** (`Format`): Validation of Format commands under different locking states (e.g., Cryptographic Erase).

    - **Sanitize** (`Sanitize`): Interaction between NVMe Sanitize and Opal security boundaries.

  

## 🏗️ Architecture

  

This project follows a modular "State-Based" testing architecture to maximize reuse:

  

1. **Environment (`/environment`)**:

   > Defines the physical namespace configuration (e.g., "Single Namespace", "No Namespace").

  

2. **Preconditions (`/preconditions`)**:

   > Defines the logical security state required before a test begins (e.g., "Opal Initialized", "Range 1 Write Locked").

  

3. **Test Cases (`/test_cases`)**:

   > The actual execution steps. Each test case declares its required Environment and Preconditions.

  

## Directory Structure

  

The project is organized into three main components:

  

```text

CNL/

├── environment/      # Physical/Namespace configurations (e.g., Single NS, No NS)

├── preconditions/    # Logical/Security states (e.g., Opal Initialized, Range Assigned)

└── test_cases/       # Executable test scenarios organized by feature

    ├── Assign/       # Range Assignment tests

    ├── Format/       # Format behavior under Opal

    ├── LockingSet/   # Locking state tests

    ├── Mgmt/         # Namespace Mgmt behavior under Opal

    └── ...