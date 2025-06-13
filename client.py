# client.py
import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD

class OdooRPCClient:
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USER
        self.password = ODOO_PASSWORD
        self.uid = self.login()

    def _rpc_call(self, service, method, args):
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args
            },
            "id": 1
        }
        response = requests.post(self.url, json=payload).json()
        if "error" in response:
            from pprint import pprint
            pprint(response["error"])  # tampilkan error-nya biar terbaca
            raise Exception(response["error"])
            
        return response["result"]

    def login(self):
        return self._rpc_call("common", "login", [self.db, self.username, self.password])

    def execute_kw(self, model, method, args, kwargs=None):
        return self._rpc_call("object", "execute_kw", [
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs or {}
        ])
