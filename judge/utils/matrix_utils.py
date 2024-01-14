import hmac, hashlib, requests


class MatrixUtils:
    shared_secret = "8c98df16746f1ced0d1ca089c6fdee15e4861628d1731abd2f0d7cb5c4cfce54f9985b8f2a5c4381104662a25d7f69942f2b32d5293512c850d2e5532018e485".encode()
    access_token = "syt_YWRtaW4_yAnimkNblaUUurzPMHno_05zH94"
    nonce = ""

    def __init__(self) -> None:
        pass

    def generate_mac(self, user, password, admin=False, user_type=None):
        mac = hmac.new(
            key=self.shared_secret,
            digestmod=hashlib.sha1,
        )

        mac.update(self.nonce.encode("utf8"))
        mac.update(b"\x00")
        mac.update(user.encode("utf8"))
        mac.update(b"\x00")
        mac.update(password.encode("utf8"))
        mac.update(b"\x00")
        mac.update(b"admin" if admin else b"notadmin")
        if user_type:
            mac.update(b"\x00")
            mac.update(user_type.encode("utf8"))

        return mac.hexdigest()

    def get_nonce(self):
        self.nonce = requests.get(
            "http://localhost:8008/_synapse/admin/v1/register"
        ).json()["nonce"]

    def create_account(self, username, displayname, password, admin=False):
        self.get_nonce()
        payload = {}
        payload["nonce"] = self.nonce
        payload["username"] = username
        payload["password"] = password
        payload["admin"] = admin
        payload["displayname"] = displayname
        payload["mac"] = self.generate_mac(username, password)
        response = requests.post(
            "http://localhost:8008/_synapse/admin/v1/register", json=payload
        )
        return response

    def get_users(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        return requests.get(
            "http://localhost:8008/_synapse/admin/v2/users", headers=headers
        ).content

    def change_password(self, username, new_password):
        return requests.put(
            f"http://localhost:8008/_synapse/admin/v2/users/@{username}:tnhoj",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"password": new_password},
        )

    def create_room(self, room_name: str, space: bool = True):
        cc = {"m.federate": False}
        if space:
            cc["type"]="m.space"
        return requests.post(
            "http://localhost:8008/_matrix/client/v3/createRoom",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "creation_content": cc,
                "name": room_name,
                "preset": "private_chat",
                "room_alias_name": room_name.lower().replace(" ", "_"),
            },
        )

    def add_user(self, username, room_name: str):
        return requests.post(
            f"http://localhost:8008/_synapse/admin/v1/join/%23{room_name.lower().replace(' ','_')}:tnhoj",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"user_id": f"@{username}:tnhoj"},
        )

    def delete_room(self, room_name: str):
        return requests.delete(
            f'http://localhost:8008/_synapse/admin/v1/rooms/%23{room_name.lower().replace(" ","_")}:tnhoj',
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"block": True, "purge": True},
        )

    def ban_user_from_room(self, room_name: str, username: str, reason: str):
        return requests.post(
            f'http://localhost:8008/_matrix/client/v3/rooms/%23{room_name.lower().replace(" ","_")}:tnhoj/ban',
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"reason": reason, "user_id": f"@{username}:tnhoj"},
        )

    def delete_user(self, username):
        return requests.post(
            f"http://localhost:8008/_synapse/admin/v1/deactivate/@{username}:tnhoj",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"erase": True},
        )

    def kick_user(self, room_name: str, username: str, reason: str):
        return requests.post(
            f"http://localhost:8008/_matrix/client/v3/rooms/%23{room_name.lower().replace(' ','_')}:tnhoj/kick",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"reason": reason, "user_id": f"@{username}:tnhoj"},
        )
