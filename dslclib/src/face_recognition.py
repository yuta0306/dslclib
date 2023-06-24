from dslclib.src.base import BaseClient
import json
import re
from dataclasses import dataclass
from typing import Literal, Callable
from collections import Counter


@dataclass
class EmotionType:
    Neutral: str = "neutral"
    Happiness: str = "happiness"
    Surprise: str = "surprise"
    Sadness: str = "sadness"
    Anger: str = "anger"
    Disgust: str = "disgust"
    fear: str = "fear"


class FaceRecognitinClient(BaseClient):
    """FaceRecognitionClient
    
    Attributes
    ----------
    ip: str
    port: int
    sock: socket.socket
    """
    def __init__(self, ip: str | None = None, port: int = 4500) -> None:
        super().__init__(ip, port)

    def receive_line(self) -> None:
        received = self.sock.recv(128).decode()
        return str(received)
    
    @staticmethod
    def summarize_times(
        data: list[tuple[float, str, float]],
        times: int = 10,
        strategy: Literal["majority", "latest"] = "majority",
    ) -> tuple[bool, float | None, str | None, float | None]:
        """
        Parameters
        ----------
        data: list[tuple[float, str, float]]
            各時刻における感情認識結果がプールされたリスト
        times: int, default = 10
            何時刻分プールしたら要約するか
        strategy: str, default = 'majority'
            majorityならば多数決、latestならば最新の認識結果を認識結果とする
        """
        if len(data) <= times:
            return False, None, None, None
        
        timestamps, emotions, scores = zip(*data)
        if strategy == "majority":
            counter = Counter(emotions)
            emotion = counter.most_common(1)[0][0]
            timestamp = timestamps[-1]
            scores = [s for e, s in zip(emotions, scores) if e == emotion]
            score = sum(scores) / len(scores)
        elif strategy == "latest":
            emotion = emotions[-1]
            timestamp = timestamps[-1]
            score = scores[-1]
        else:
            raise ValueError("strategyの引数には、`majority`と`latest`のみが有効です")
        
        return True, timestamp, emotion, score
    
    @staticmethod
    def summarize_timestamps(
        data: list[tuple[float, str, float]],
        sec: float = 1,
        strategy: Literal["majority", "latest"] = "majority",
    ) -> tuple[bool, float | None, str | None, float | None]:
        """
        Parameters
        ----------
        data: list[tuple[float, str, float]]
            各時刻における感情認識結果がプールされたリスト
        sec: float, default = 1
            何秒プールしたら認識結果を要約するか
        strategy: str, default = 'majority'
            majorityならば多数決、latestならば最新の認識結果を認識結果とする
        """
        if data[-1][0] - data[0][0] < sec:
            return False, None, None, None
        
        timestamps, emotions, scores = zip(*data)
        if strategy == "majority":
            counter = Counter(emotions)
            emotion = counter.most_common(1)[0][0]
            timestamp = timestamps[-1]
            scores = [s for e, s in zip(emotions, scores) if e == emotion]
            score = sum(scores) / len(scores)
        elif strategy == "latest":
            emotion = emotions[-1]
            timestamp = timestamps[-1]
            score = scores[-1]
        else:
            raise ValueError("strategyの引数には、`majority`と`latest`のみが有効です")
        
        return True, timestamp, emotion, score

    def listen(
        self,
        func: Callable | None = None
    ) -> tuple[float | None, str, float | None]:
        """
        感情認識サーバとのソケット通信をするメソッド

        Parameters
        ----------
        func: Callable, optional
            funcに何も与えない場合、感情認識結果が取得された時点ですぐに結果を返します。
            ただし、認識結果の応答が早く、安定しないこともあることから、funcを与えないことは推奨しません。
            カスタムでfuncを定義してもよいですが、簡易的な静的メソッドとして`summarize_times`と`summarize_timestamps`を用意してあります。
            カスタムで定義する場合の要件は以下です。
            入力: list[tuple[float, str, float]]
                リストの各要素は各時点での認識結果であり、
                認識結果は (timestamp, emotion_class, emotion_score)です。
            出力: tuple[bool, float | None, str | None, float | None]
                (要約した認識結果を返す=True | まだプールする=False, timestamp, emotion_class, emotion_score)
            以上の要件を満たした関数を設計してください。

        Returns
        -------
        tuple[float | None, str, float | None]
        """
        do_return: bool = False
        pool: list[tuple[float, str, float]]= []
        while True:
            received = self.receive_line()
            if not re.search(r"^\{[^\n]+\}\n", received):
                continue
            
            data = json.loads(received)
            if func is None:
                return data["timestamp"], data["emotion_class"], data["emotion_score"]
            
            pool.append(tuple(data.values()))
            do_return, timestamp, emotion, score = func(data=pool)
            if do_return:
                if not isinstance(emotion, str):
                    raise TypeError(f"出力する感情クラスは`str`のみですが、{type(str)}があたえられています。`func`を要件を満たすように設計してください。")
                return timestamp, emotion, score
        

if __name__ == "__main__":
    client = FaceRecognitinClient()
    for i in range(10):
        print(client.listen(FaceRecognitinClient.summarize_times))

    for _ in range(10):
        print(client.listen(FaceRecognitinClient.summarize_timestamps))

    client.close()