import json
from typing import Optional
import time
import threading
import warnings

from dslclib.src.base import BaseClient


class SpeechConfig(str):
    """
    SpeechConfig

    スピーチの設定の入力から，文字列を生成するstr継承クラス
    """

    def __new__(
        cls,
        text: str,
        engine: str = "POLLY",
        speaker: str = "Mizuki",
        pitch: int = 100,
        volume: int = 100,
        speed: int = 100,
        vocal_tract_length: int = 0,
        duration_information: bool = False,
        speechmark: bool = False,
    ):
        """SpeechConfig

        Parameters
        ----------
        text: str
        engine: str, default = 'POLLY'
        speaker: str, default = 'Mizuki'
        pitch: int, default = 100
        volume: int, default = 100
        speed: int, default = 100
        vocal_tract_length: int, default = 0
        duration_information: bool, default = False
        speechmark: bool, default = False
        """
        data = {
            "engine": engine,
            "speaker": speaker,
            "pitch": pitch,
            "volume": volume,
            "speed": speed,
            "vocal-tract-length": vocal_tract_length,
            "duration-information": duration_information,
            "speechmark": speechmark,
            "text": text,
        }
        return super().__new__(cls, json.dumps(data, ensure_ascii=False))


class QueueSupervisor(threading.Thread):
    def __init__(self, client, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.should_stop = threading.Event()
    
    def run(self):
        while not self.should_stop.wait(0):
            try:
                self.client.monitor_queue()
            except ConnectionAbortedError:
                break
        print("QueueSupervisorはシャットダウンされました。")

    def kill(self):
        self.should_stop.set()


class Text2SpeechClient(BaseClient):
    """Text2SpeechClient

    音声にしたい発話テキストをソケットに送信するクライアント
    """

    def __init__(
            self,
            ip: Optional[str] = None,
            port: int = 3456,
        ) -> None:
        """
        Parameters
        ----------
        ip: str, optional
            ipアドレス．

            デフォルトはNoneであり，Noneが与えられた時，127.0.0.1(ローカルホスト)を指定し，
            もし，docker内でこのモジュールが立ち上がっていた場合，自動でそれが認識され，host.docker.internalを指定する．

            host.docker.internalは，docker内からローカルホストのポートに接続するために必要である．
        port: int = 3456
            ソケット通信を行うポート．

        Returns
        -------

        Examples
        --------
        >>> client = Text2SpeechClient()
        ipがNoneだったため、127.0.0.1をipアドレスとして設定します。
        >>> client
        Socket(
            ip   = 127.0.0.1
            port = 3456
        )
        >>>
        """
        super().__init__(ip, port)
        self.queue = list()
        self.supervisor = QueueSupervisor(self, daemon=False)
        self.supervisor.start()

    def close(self) -> None:
        self.supervisor.should_stop.set()
        return super().close()

    def monitor_queue(self):
        """
        キューを監視し、合成音声の再生を終えたのちにキューからコマンドを削除するメソッド
        **注意**: このメソッドは`self.supervisor`から呼び出されることを推奨する
        """
        received = json.loads(str(self.sock.recv(4096).decode()))
        if "result" in list(received.keys()) and received["result"] == "success-end":
            self.queue.pop(0)

    def is_speaking(self) -> bool:
        """
        音声を再生中かどうかを確認するメソッド
        """
        self.sock.send(json.dumps({"engine": "ISSPEAKING"}).encode())
        received = json.loads(str(self.sock.recv(1024).decode()))
        if "isSpeaking" in list(received.keys()):
            return received["isSpeaking"] == True
        return False
    
    def stop_speaking(self) -> None:
        self.sock.send(json.dumps({"engine": "STOP"}).encode())
    
    def wait_finish_speaking(self, timeout: float = -1.0) -> None:
        if timeout > 0:
            raise NotImplementedError
        while True:
            received = json.loads(str(self.sock.recv(4096).decode()))
            if "result" in list(received.keys()) and received["result"] == "success-end":
                break

    def speech(
        self,
        text: str,
        engine: str = "POLLY",
        speaker: str = "Mizuki",
        pitch: int = 100,
        volume: int = 100,
        speed: int = 100,
        vocal_tract_length: int = 0,
        duration_information: bool = False,
        speechmark: bool = False,
        max_num_queue: int = 1,
        wait_queue: bool = False,
    ) -> None:
        """
        音声にしたい発話テキストと発話音声の設定を入力としてソケットに送信する関数

        Parameters
        ----------
        text: str
            発話テキスト
        engine: str, default = 'POLLY'
            音声エンジン
        speaker: str, default = 'Mizuki'
            話者
        pitch: int, default = 100
            ピッチ
        volume: int, default = 100
            ボリューム
        speed: int, default = 100
            発話スピード
        vocal_tract_length: int, default = 0
        duration_information: bool, default = False
        speechmark: bool, default = False
            スピーチマークが含まれるかどうか
        max_num_queue: int, default = 1
            TTSコマンドのキューを最大いくつまでプールできるか
        wait_queue: bool, default = False
            max_num_queueのキュー数を超えた場合、キューが空くまで処理を待つかどうか。
            `wait=False`に設定した場合、TTSのコマンドをキューにスタックせずに終了する。

        Returns
        -------
        """
        if len(self.queue) >= max_num_queue:
            if wait_queue:
                warnings.warn("TTSコマンドの最大キュー数を超えたため、キューが空くまで待機します。")
                while len(self.queue) >= max_num_queue:
                    time.sleep(0.05)
            else:
                warnings.warn(f"TTSコマンドの最大キュー数を超えたため、`{text}`は音声合成されません。", UserWarning)
                return
        
        speech = SpeechConfig(
            text=text,
            engine=engine,
            speaker=speaker,
            pitch=pitch,
            volume=volume,
            speed=speed,
            vocal_tract_length=vocal_tract_length,
            duration_information=duration_information,
            speechmark=speechmark,
        )
        command = speech + "\n"
        self.sock.send(command.encode())
        self.queue.append(command)


if __name__ == "__main__":
    import time

    client = Text2SpeechClient()
    client.speech("あーーーー", speed=50)
    time.sleep(3)
    client.speech("すみません", volume=20)
    time.sleep(3)
    client.speech("こんにちは")

    client.close()
