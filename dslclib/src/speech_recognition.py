from dslclib.src.base import BaseClient
import re
from dataclasses import dataclass
from typing import Literal

@dataclass
class STTRecognitionType:
    InterimResult = "interimresult"
    Result = "result"

class SpeechRecognitionClient(BaseClient):
    """SpeechRecognitionClient
    Attributes
    ----------
    ip: str
    port: int
    sock: socket.socket
    """
    def __init__(self, ip: str | None = None, port: int = 8888) -> None:
        """SpeechRecognitionClient

        Google Speech Recognition APIのTCPソケット通信を扱うクライアント

        Parameters
        ----------
        ip: str | None, optional
        port: int, default = 8888
        """
        super().__init__(ip, port)
        self.sock.send("start\n".encode())

    def close(self) -> None:
        self.sock.send("stop\n".encode())
        return super().close()
    
    def receive_line(self) -> str:
        received = self.sock.recv(4096).decode()
        return str(received)
    
    def listen(self, interim: bool = True) -> tuple[Literal["interimresult", "result"], str]:
        """
        データがたまってからデータを出力するメソッド
        interimをTrueにすると、発話中でもその時点の認識結果を出力する
        interimをFalseにすると、発話終了の上での認識結果のみを出力する

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
                    return STTRecognitionType.InterimResult, matching_result.group(1)
                
            matching_result = re.search(r'^result:([^\n]+)\n', received)
            if matching_result is not None:
                return STTRecognitionType.Result, matching_result.group(1)
            

if __name__ == "__main__":
    client = SpeechRecognitionClient()
    for _ in range(20):
        print(client.listen())
    
    client.close()

