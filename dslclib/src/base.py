import socket
from typing import Optional


class BaseClient(object):
    """BaseClient"""

    def __init__(self, ip: Optional[str] = None, port: int = 8888) -> None:
        """
        ソケット通信をする各モジュールのベースクラス

        各モジュールはこのBaseClientを継承する

        Parameters
        ----------
        ip: str, optional
            ipアドレス．

            デフォルトはNoneであり，Noneが与えられた時，127.0.0.1(ローカルホスト)を指定し，
            もし，docker内でこのモジュールが立ち上がっていた場合，自動でそれが認識され，host.docker.internalを指定する．

            host.docker.internalは，docker内からローカルホストのポートに接続するために必要である．
        port: int = 8888
            ソケット通信を行うポート．

            BaseClientを継承するときには，そのクラスに合わせてportのデフォルトを書き換える．

        Returns
        -------

        Examples
        --------
        >>> client = BaseClient()
        ipがNoneだったため、127.0.0.1をipアドレスとして設定します。
        >>> client
        Socket(
            ip   = 127.0.0.1
            port = 8888
        )
        >>>
        >>> client = BaseClient(ip='localhost', port=3333)
        >>> client
        Socket(
            ip   = localhost
            port = 3333
        )
        """
        self.sock: socket.socket = socket.socket()
        self.ip: str = "127.0.0.1"
        if ip is not None:
            self.ip = ip
        else:
            try:
                with open("/etc/hosts", "r") as f:
                    for line in f.readlines():
                        if "host.docker.internal" in line:
                            self.ip = (
                                "host.docker.internal"  # dockerにホストのポートを接続許可した時に上書き
                            )
                            break
            except Exception:  # /etc/hostsが存在しないとき
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
        """ipアドレスのportに接続する．

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> client = BaseClient()
        >>> client.connect()

        """
        self.sock.connect((self.ip, self.port))

    def close(self) -> None:
        """ipアドレスのportへの接続を切る．

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> client = BaseClient()
        >>> client.connect()
        >>> client.close()

        """
        self.sock.close()
