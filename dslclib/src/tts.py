from dslclib.src.base import BaseClient
from typing import Literal
import json


class SpeechConfig(str):
    """
    SpeechConfig

    Attributes
    ----------
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
    ) -> None:
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
            "text": text
        }
        return super().__new__(cls, json.dumps(data))


class Text2SpeechClient(BaseClient):
    """Text2SpeechClient
    Attributes
    ----------
    ip: str
    port: int
    sock: socket.socket
    """
    def __init__(self, ip: str | None = None, port: int = 3456) -> None:
        """Text2SpeechClient

        音声にしたい発話テキストをソケットに送信するクライアント

        Parameters
        ----------
        ip: str | None, optional
        port: int, default = 3456
        """
        super().__init__(ip, port)

    def close(self) -> None:
        return super().close()
    
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
    ) -> tuple[Literal["interimresult", "result"], str]:
        """
        音声にしたい発話テキストと発話音声の設定を入力としてソケットに送信する関数

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
        speech = SpeechConfig(
            text=text,
            engine=engine,
            speaker=speaker,
            pitch=pitch,
            volume=volume,
            speed=speed,
            vocal_tract_length=vocal_tract_length,
            duration_information=duration_information,
            speechmark=speechmark
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

