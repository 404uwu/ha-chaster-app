# ha-chaster

An unofficial Home Assistant Integration for [Chaster.app](https://chaster.app/).

## Features

- Adds Data like "Total Time Locked", "Duration Until Unlock Time", "Is Lock Frozen", and more to Home Assistant
- Exposes a service (`update_lock_duration`) to add time to the lock's duration (or remove time if you are the Keyholder)

## Setup

TODO: Add HACS installation steps
After adding this repository to HACS and installing the Integration, you can use Home Assistant's integrations page to set-up a lock.

### Connecting with Chaster

Currently the integration is only usable via a personal token. For that you first need to [request developer access from chaster](https://chaster.app/developers) (scroll down the page and find the **"request API access" button**). The process is automated and you should receive access after 1 or 2 minutes.

After you have developer access, go to the [developer interface](https://chaster.app/developers/applications) and **create an application**. Enter some name and leave the Redirect URI blank.

Now when you go to your newly created application in the sidebar click on **"Tokens"**, where you can find or generate your "Developer token".

> [!IMPORTANT]
> Do not mistake the "secret key" for the "developer token". The developer token can be found in the left-hand sidebar under **"Tokens"**.

The Lock ID can be found on Chaster in the Lock Settings' URL. If you go to your lock in Chaster and click on "Settings", the URL in your browser should look like "chaster.app/locks/abc123def456/settings". **In that case "abc123def456" would be your Lock ID.**

When setting up the integration in Home Assistant, you need to enter your generated API Token and the Lock ID and are good to go.
