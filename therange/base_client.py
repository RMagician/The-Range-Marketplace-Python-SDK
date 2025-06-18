class BaseClient:
    def __init__(self, auth_client):
        self.auth = auth_client

    def _post(self, endpoint, payload, include_supplier_id=True, include_mode=True):
        params = {}
        if include_supplier_id and self.auth.supplier_id:
            params["supplier_id"] = self.auth.supplier_id
        if include_mode and self.auth.mode:
            payload["mode"] = self.auth.mode

        url = f"{self.auth.base_url}{endpoint}"
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)

        response = self.auth.session.post(url, json=payload)
        if response.status_code == 401:
            raise PermissionError("Not authenticated.")
        elif response.status_code == 400:
            raise ValueError(f"Bad request: {response.text}")

        response.raise_for_status()
        return response.json()
