import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Literal, Optional

from dslclib.src.base import BaseClient


@dataclass
class EmotionType:
    """EmotionType
    感情認識サーバが出力する感情値を定義したデータクラス
    """

    Neutral: str = "neutral"
    Happiness: str = "happiness"
    Surprise: str = "surprise"
    Sadness: str = "sadness"
    Anger: str = "anger"
    Disgust: str = "disgust"
    fear: str = "fear"


class FaceRecognitionClient(BaseClient):
    """FaceRecognitionClient

    ユーザの感情を認識するサーバとソケット通信するクライアント．
    （これから顔の向きに対応する予定）
    """

    def __init__(self, ip: Optional[str] = None, port: int = 4500) -> None:
        """
        Parameters
        ----------
        ip: str, optional
            ipアドレス．

            デフォルトはNoneであり，Noneが与えられた時，127.0.0.1(ローカルホスト)を指定し，
            もし，docker内でこのモジュールが立ち上がっていた場合，自動でそれが認識され，host.docker.internalを指定する．

            host.docker.internalは，docker内からローカルホストのポートに接続するために必要である．
        port: int = 4500
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
            port = 4500
        )
        >>>
        """
        super().__init__(ip, port)

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
        received = str(self.sock.recv(128).decode())
        return received

    @staticmethod
    def summarize_times(
        data: list[tuple[float, str, float]],
        times: int = 10,
        strategy: Literal["majority", "latest"] = "majority",
    ) -> tuple[bool, Optional[float], Optional[str], Optional[float]]:
        """
        感情認識サーバから得たtimes回の結果を集約し，strategyに則ったアルゴリズムで感情値を決定する静的メソッド．

        strategyはmajorityを推奨する．

        Parameters
        ----------
        data: list[tuple[float, str, float]]
            各時刻における感情認識結果がプールされたリスト
        times: int, default = 10
            何回分の結果をプールしたら要約するか
        strategy: str, default = 'majority'
            majorityならば多数決、latestならば最新の認識結果を認識結果とする

        Returns
        -------
        tuple[bool, Optional[float], Optional[str], Optional[float]]
            (戻り値があるか？, timestamp, 感情値, 感情スコア)

            1つ目の要素がTrueならば，指定回数分の結果を用いて感情値を決定していることを示す．
            Falseならば，回数分に満たないため，さらにプールを要求することを示す．
        """
        if len(data) <= times:
            return False, None, None, None

        timestamps, emotions, scores_ = zip(*data)
        scores = list(scores_)
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
    ) -> tuple[bool, Optional[float], Optional[str], Optional[float]]:
        """
        感情認識サーバから得たsec秒分の結果を集約し，strategyに則ったアルゴリズムで感情値を決定する静的メソッド．

        strategyはmajorityを推奨する．

        Parameters
        ----------
        data: list[tuple[float, str, float]]
            各時刻における感情認識結果がプールされたリスト
        sec: float, default = 1
            何秒プールしたら認識結果を要約するか
        strategy: str, default = 'majority'
            majorityならば多数決、latestならば最新の認識結果を認識結果とする

        Returns
        -------
        tuple[bool, Optional[float], Optional[str], Optional[float]]
            1つ目の要素がTrueならば，指定回数分の結果を用いて感情値を決定していることを示す．
            Falseならば，回数分に満たないため，さらにプールを要求することを示す．
        """
        if data[-1][0] - data[0][0] < sec:
            return False, None, None, None

        timestamps, emotions, scores_ = zip(*data)
        scores = list(scores_)
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
        self, func: Optional[Callable] = None
    ) -> tuple[Optional[float], str, Optional[float]]:
        """
        感情認識サーバとのソケット通信をするメソッド

        Parameters
        ----------
        func: Callable, optional
            funcに何も与えない場合、感情認識結果が取得された時点ですぐに結果を返します.

            ただし、認識結果の応答が早く、安定しないこともあることから、funcを与えないことは推奨しません.

            カスタムでfuncを定義してもよいですが、簡易的な静的メソッドとして`summarize_times`と`summarize_timestamps`を用意してあります.
            カスタムで定義する場合の要件は以下です.
            入力: list[tuple[float, str, float]]

            リストの各要素は各時点での認識結果であり、
            認識結果は (timestamp, emotion_class, emotion_score)です.

            出力: tuple[bool, Optional[float], Optional[str], Optional[float]]

            (要約した認識結果を返す=True | まだプールする=False, timestamp, emotion_class, emotion_score)
            以上の要件を満たした関数を設計してください.

        Returns
        -------
        tuple[Optional[float], str, Optional[float]]
        """
        do_return: bool = False
        pool: list[tuple[float, str, float]] = []
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
                    raise TypeError(
                        f"出力する感情クラスは`str`のみですが、{type(str)}があたえられています。`func`を要件を満たすように設計してください。"
                    )
                return timestamp, emotion, score


if __name__ == "__main__":
    client = FaceRecognitionClient()
    for i in range(10):
        print(client.listen(FaceRecognitionClient.summarize_times))

    for _ in range(10):
        print(client.listen(FaceRecognitionClient.summarize_timestamps))

    client.close()
