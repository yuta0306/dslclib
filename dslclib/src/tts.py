import json
from typing import Optional

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
        return super().__new__(cls, json.dumps(data))


class Text2SpeechClient(BaseClient):
    """Text2SpeechClient

    音声にしたい発話テキストをソケットに送信するクライアント
    """

    def __init__(self, ip: Optional[str] = None, port: int = 3456) -> None:
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
        >>> client = BodyController()
        ipがNoneだったため、127.0.0.1をipアドレスとして設定します。
        >>> client
        Socket(
            ip   = 127.0.0.1
            port = 3456
        )
        >>>
        """
        super().__init__(ip, port)

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


        Returns
        -------
        """
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


if __name__ == "__main__":
    import time

    client = Text2SpeechClient()
    client.speech("あーーーー", speed=50)
    time.sleep(3)
    client.speech("すみません", volume=20)
    time.sleep(3)
    client.speech("こんにちは")

    client.close()
