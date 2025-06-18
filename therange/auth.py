import requests
from http.cookies import SimpleCookie
from .config import Config

class AuthClient:
    def __init__(self, username, password, config: Config):
        """
        Initialize AuthClient.
        
        Args:
            username: The username for authentication
            password: The password for authentication
            config: Configuration object specifying the environment to use
        """
        self.username = username
        self.password = password
        self.config = config
        
        self.session = requests.Session()
        self.mode = None
        self.supplier_id = None
        self.ksi = None
        self.base_url = self.config.base_url

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
