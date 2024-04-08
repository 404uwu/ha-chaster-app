import requests

from .config_flow import InvalidAuth, NotPermitted
from .const import CHASTER_API_BASEURL


class ChasterClient:
    """Client to interface with the chaster.app API."""

    def __init__(self, lock_id: str, api_token: str) -> None:
        """Initialize."""
        self.lock_id = lock_id
        self.api_token = api_token

    def fetch_lock_details(self):
        """Fetch the details of the lock."""

        lock_details_response = requests.get(
            f"{CHASTER_API_BASEURL}/locks/{self.lock_id}",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=30,
        )
        if lock_details_response.status_code == 401:
            raise InvalidAuth

        return lock_details_response.json()

    def check_connection(self):
        """Return true if the connection can be established successfully."""

        try:
            self.fetch_lock_details()
            return True
        except:
            return False

    def set_lock_is_frozen(self, is_frozen: bool):
        "Set the lock's is_frozen state."

        freeze_request_response = requests.post(
            f"{CHASTER_API_BASEURL}/locks/{self.lock_id}/freeze",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=30,
            json={"isFrozen": is_frozen},
        )

        if freeze_request_response.status_code == 401:
            raise InvalidAuth

        if freeze_request_response.status_code == 403:
            raise NotPermitted

        return freeze_request_response.json()
