import re
from dataclasses import dataclass
from typing import Literal, Optional

from dslclib.src.base import BaseClient


@dataclass
class STTRecognitionType:
    InterimResult: Literal["interimresult"] = "interimresult"
    Result: Literal["result"] = "result"


@dataclass
class OutputForSTTRecognition:
    type: Literal["interimresult", "result"]
    result: str

    def __getitem__(self, key):
        return getattr(self, key)


class SpeechRecognitionClient(BaseClient):
    """SpeechRecognitionClient

    Google Speech Recognition APIによる音声認識の結果をソケットから受け取るクライアント
    """

    def __init__(self, ip: Optional[str] = None, port: int = 8888) -> None:
        """
        Parameters
        ----------
        ip: str, optional
            ipアドレス．

            デフォルトはNoneであり，Noneが与えられた時，127.0.0.1(ローカルホスト)を指定し，
            もし，docker内でこのモジュールが立ち上がっていた場合，自動でそれが認識され，host.docker.internalを指定する．

            host.docker.internalは，docker内からローカルホストのポートに接続するために必要である．
        port: int = 8888
            ソケット通信を行うポート．

        Returns
        -------

        Examples
        --------
        >>> client = SpeechRecognitionClient()
        ipがNoneだったため、127.0.0.1をipアドレスとして設定します。
        >>> client
        Socket(
            ip   = 127.0.0.1
            port = 8888
        )
        >>>
        """
        super().__init__(ip, port)
        self.sock.send("start\n".encode())

    def close(self) -> None:
        self.sock.send("stop\n".encode())
        return super().close()

    def receive_line(self) -> str:
        """
        ソケットから受け取ったバイナリコードを文字列（utf-8）に変換するメソッド

        Parameters
        ----------

        Returns
        -------
        received: str
            ソケット通信によって受け取った値を文字列に変換したもの
        """
        received = str(self.sock.recv(4096).decode())
        return received

    def listen(self, interim: bool = True) -> OutputForSTTRecognition:
        """
        データがたまってからデータを出力するメソッド．

        interimをTrueにすると、発話中でもその時点の認識結果を出力する．

        interimをFalseにすると、発話終了の上での認識結果のみを出力する．

        発話中における出力例
        ('interimresult', 'あいう')

        発話終了における出力例
        ('result', 'あいうえお')

        Parameters
        ----------
        interim: bool, default = True
            Trueのときは、発話中でもその時点でたまった認識結果を出力する

        Returns
        -------
        tuple[Literal["interimresult", "result"], str]
            (状態, 認識結果)
        """
        while True:
            received = self.receive_line()
            if interim:  # 発話中でも出力するかどうか
                matching_result = re.search(r"^interimresult:([^\n]+)\n", received)
                if matching_result is not None:
                    return OutputForSTTRecognition(
                        type=STTRecognitionType.InterimResult,
                        result=matching_result.group(1),
                    )

            matching_result = re.search(r"^result:([^\n]+)\n", received)
            if matching_result is not None:
                return OutputForSTTRecognition(
                    type=STTRecognitionType.Result,
                    result=matching_result.group(1),
                )


if __name__ == "__main__":
    client = SpeechRecognitionClient()
    for _ in range(20):
        print(client.listen())

    client.close()
