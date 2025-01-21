# MI Inventory

## Overview
This script retrieves and exports information about managed identities (both system-assigned and user-assigned) across all subscriptions in an Azure tenant. The output is saved as a CSV file.

## Features
- Collects user-assigned managed identities and their associated resources.
- Identifies system-assigned managed identities and their associated resource types.
- Supports multi-subscription scanning within the tenant.
- Outputs the data to a CSV file.

## Prerequisites
1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure the Azure CLI is installed and logged in:
   ```bash
   az login
   ```

3. Assign the necessary Azure permissions for the authenticated user:
   - At the least, the `Reader` role is required on all of the subscriptions.

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/astrix-security/MI-Inventory.git
   cd MI-Inventory
   ```

2. Run the script:
   ```bash
   python mi-inventory.py
   ```

3. The script will output a CSV file named `managed_identities.csv` containing the following columns:
   - `Name`: The name of the managed identity.
   - `Managed Identity Type`: Either `User Assigned` or `System Assigned`.
   - `Subscription`: The subscription name.
   - `System Assigned Managed Identity Resource Type`: The resource type of the system-assigned identity.
   - `User Managed Identity Associated Resource Count`: Number of resources associated with the user-assigned identity.
   - `User Assigned Managed Identity Associated Resources`: List of associated resources.

## License
This project is licensed under the GPL 3 License - see the LICENSE file for details.


