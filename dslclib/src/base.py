import socket

class BaseClient(object):
    """BaseClient
    ソケット通信をする各モジュールのベースクラス
    """
    def __init__(self, ip: str | None = None, port: int = 8888) -> None:
        self.sock: socket.socket = socket.socket()
        self.ip: str = "127.0.0.1"
        if ip is not None:
            self.ip = ip
        else:
            try:
                with open("/etc/hosts", "r") as f:
                    for line in f.readlines():
                        if "host.docker.internal" in line:
                            self.ip = "host.docker.internal"  # dockerにホストのポートを接続許可した時に上書き
                            break
            except:  # /etc/hostsが存在しないとき
                pass
            finally:
                print(f"ipがNoneだったため、{self.ip}をipアドレスとして設定します。")

        self.port: int = port

        self.connect()

    def __repr__(self) -> str:
        return f"""Socket(
            ip   = {self.ip}
            port = {self.port}
        )"""
    
    def connect(self) -> None:
        self.sock.connect((self.ip, self.port))

    def close(self) -> None:
        self.sock.close()
