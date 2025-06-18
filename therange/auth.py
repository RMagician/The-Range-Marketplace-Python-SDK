import requests
from http.cookies import SimpleCookie

class AuthClient:
    def __init__(self, username, password, test=False):
        self.username = username
        self.password = password
        self.test = test
        self.session = requests.Session()
        self.mode = None
        self.supplier_id = None
        self.ksi = None
        self.base_url = "https://uatsupplier.rstore.com/rest/" if test else "https://supplier.rstore.com/rest/"

    def authenticate(self):
        url = self.base_url + "authenticate.api"
        response = self.session.post(url, json={"user": self.username, "pass": self.password})
        if response.status_code == 401:
            raise PermissionError("Unauthorized: Invalid credentials")
        elif response.status_code == 400:
            raise ValueError(f"Bad request: {response.text}")
        response.raise_for_status()

        cookie = SimpleCookie()
        cookie.load(response.headers.get("Set-Cookie", ""))
        if "ksi" not in cookie:
            raise RuntimeError("Authentication failed: 'ksi' cookie missing")
        self.ksi = cookie['ksi'].value
        self.session.cookies.set("ksi", self.ksi)

        data = response.json()
        self.mode = data.get("mode")
        self.supplier_id = str(data.get("supplier_id"))
        return data
