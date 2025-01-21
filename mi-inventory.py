import csv
import re

import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient


def get_associated_resources(
    subscription_id, resource_group, identity_name, credential
):

    """Retrieve associated resources for a User Assigned Managed Identity."""

    url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identity_name}/listAssociatedResources?api-version=2021-09-30-preview"
    token = credential.get_token("https://management.azure.com/.default").token
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return [res["id"] for res in response.json().get("value", [])]
    else:
        print(
            f"Failed to fetch associated resources for {identity_name}: {response.status_code} - {response.text}"
        )
        return []


def get_user_assigned_identities(subscription_id, subscription_name, credential):

    """Retrieve user-assigned managed identities."""

    msi_client = ManagedServiceIdentityClient(credential, subscription_id)
    user_assigned_identities = []

    for identity in msi_client.user_assigned_identities.list_by_subscription():
        identity_id_parts = identity.id.split("/")
        resource_group = identity_id_parts[
            identity_id_parts.index("resourcegroups") + 1
        ]
        identity_name = identity.name
        associated_resources = get_associated_resources(
            subscription_id, resource_group, identity_name, credential
        )

        user_assigned_identities.append(
            {
                "Name": identity.name,
                "Managed Identity Type": "User Assigned",
                "Subscription": subscription_name,
                "System Assigned Managed Identity Resource Type": "",
                "User Managed Identity Associated Resource Count": len(
                    associated_resources
                ),
                "User Assigned Managed Identity Associated Resources": "; ".join(
                    associated_resources
                )
                if associated_resources
                else "None",
            }
        )

    return user_assigned_identities


def get_system_assigned_identities(subscription_id, subscription_name, credential):

    """Retrieve system-assigned managed identities."""

    resource_client = ResourceManagementClient(credential, subscription_id)
    system_assigned_identities = []

    for resource in resource_client.resources.list():
        if resource.identity and resource.identity.type == "SystemAssigned":
            match = re.search(r"providers/[^/]+/([^/]+)/", resource.id)
            resource_type = match.group(1) if match else "Unknown"
            system_assigned_identities.append(
                {
                    "Name": resource.name,
                    "Managed Identity Type": "System Assigned",
                    "Subscription": subscription_name,
                    "System Assigned Managed Identity Resource Type": resource_type,
                    "User Managed Identity Associated Resource Count": 0,
                    "User Assigned Managed Identity Associated Resources": "",
                }
            )

    return system_assigned_identities


def get_managed_identities(subscription_id, subscription_name):

    """Retrieve both user-assigned and system-assigned managed identities."""

    credential = DefaultAzureCredential()
    managed_identities = []
    managed_identities.extend(
        get_user_assigned_identities(subscription_id, subscription_name, credential)
    )
    managed_identities.extend(
        get_system_assigned_identities(subscription_id, subscription_name, credential)
    )

    return managed_identities


def get_all_subscriptions():

    """Retrieve all subscriptions for the tenant."""

    credential = DefaultAzureCredential()
    subscription_client = SubscriptionClient(credential)

    return [
        (sub.subscription_id, sub.display_name)
        for sub in subscription_client.subscriptions.list()
    ]


def save_to_csv(managed_identities, output_file):

    """Save managed identities to a CSV file."""

    fieldnames = [
        "Name",
        "Managed Identity Type",
        "Subscription",
        "System Assigned Managed Identity Resource Type",
        "User Managed Identity Associated Resource Count",
        "User Assigned Managed Identity Associated Resources",
    ]
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(managed_identities)


if __name__ == "__main__":
    output_file = "managed_identities.csv"
    print("Fetching subscriptions...")
    subscriptions = get_all_subscriptions()
    all_managed_identities = []
    for subscription_id, subscription_name in subscriptions:
        print(
            f"Fetching managed identities for subscription: {subscription_name} ({subscription_id})"
        )
        managed_identities = get_managed_identities(subscription_id, subscription_name)
        all_managed_identities.extend(managed_identities)

    print(f"Saving managed identities to {output_file}...")
    save_to_csv(all_managed_identities, output_file)
    print(f"Managed identities saved to {output_file}.")
