import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Literal, Optional

from dslclib.src.base import BaseClient


@dataclass
class Rotation:
    """Rotation
    ユーザの顔の向きを示すデータクラス

    各アトリビュートは以下の通りです．

    - pitch: 上下(上がプラス)
    - roll: 回転．首をかしげる動き(右にかしげるとプラス)
    - yaw: 横向き(左がプラス)
    """

    pitch: float
    roll: float
    yaw: float


@dataclass
class OutputForFaceRecognition:
    """OutputForFaceRecognition
    感情認識サーバのクライアントが出力するデータクラス

    各アトリビュートは以下の通りです．

    - summarized: 出力結果が，funcによって，一定時刻分の認識結果を要約されたものであるかどうか
    - timestamp: タイムスタンプ
    - emotion: 認識された感情クラス
    - emotion_score: 感情クラスのスコア
    - rotations: 各時刻のRotationの情報が時系列順に含まれるリスト
    - age: 推測された年齢
    - gender: 推測された性別
    - gender_score: 推測性別のスコア
    """

    summarized: bool
    timestamp: float
    emotion: str
    emotion_score: float
    rotations: list[Rotation]
    age: Optional[int] = None
    gender: Optional[Literal["Man", "Woman"]] = None
    gender_score: Optional[float] = None

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class EmotionType:
    """EmotionType
    感情認識サーバが出力する感情値を定義したデータクラス
    """

    Neutral: Literal["neutral"] = "neutral"
    Happiness: Literal["happiness"] = "happiness"
    Surprise: Literal["surprise"] = "surprise"
    Sadness: Literal["sadness"] = "sadness"
    Anger: Literal["anger"] = "anger"
    Disgust: Literal["disgust"] = "disgust"
    Fear: Literal["fear"] = "fear"


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
        >>> client = FaceRecognitionClient()
        ipがNoneだったため、127.0.0.1をipアドレスとして設定します。
        >>> client
        Socket(
            ip   = 127.0.0.1
            port = 4500
        )
        >>>
        """
        super().__init__(ip, port)
        self.age: Optional[int] = None
        self.gender: Optional[Literal["Man", "Woman"]] = None
        self.gender_score: Optional[float] = None

    def get_user_info(
        self,
    ) -> tuple[Optional[int], Optional[Literal["Man", "Woman"]], Optional[float]]:
        return self.age, self.gender, self.gender_score

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
        received = str(self.sock.recv(256).decode())
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

    def listen(self, func: Optional[Callable] = None) -> OutputForFaceRecognition:
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
        OutputForFaceRecognition

        Examples
        --------
        >>> client = FaceRecognitionClient()
        >>> output = client.listen(FaceRecognitionClient.summarize_times)
        >>> output.emotion
        angry
        >>> output["emotion"]
        angry
        """
        do_return: bool = False
        pool: list[tuple[float, str, float]] = []
        rotations: list[Rotation] = []
        while True:
            received = self.receive_line()
            if not re.search(r"^\{[^\n]+\}\n", received):
                continue

            data = json.loads(received)
            timestamp: float = data["timestamp"]
            emotion: str = data["emotion_class"]
            score: float = data["emotion_score"]
            rot = data["rotation"]
            rotations.append(
                Rotation(pitch=rot["pitch"], roll=rot["roll"], yaw=rot["yaw"])
            )
            # user info
            if "age" in list(data.keys()):
                self.age = data["age"]
                self.gender = data["gender_class"]
                self.gender_score = data["gender_score"]

            age, gender, gender_score = self.get_user_info()
            if func is None:
                return OutputForFaceRecognition(
                    summarized=True,
                    timestamp=timestamp,
                    emotion=emotion,
                    emotion_score=score,
                    rotations=rotations,
                    age=age,
                    gender=gender,
                    gender_score=gender_score,
                )

            pool.append((timestamp, emotion, score))
            do_return, timestamp, emotion, score = func(data=pool)
            if do_return:
                if not isinstance(emotion, str):
                    raise TypeError(
                        f"出力する感情クラスは`str`のみですが、{type(str)}があたえられています。`func`を要件を満たすように設計してください。"
                    )
                return OutputForFaceRecognition(
                    summarized=True,
                    timestamp=timestamp,
                    emotion=emotion,
                    emotion_score=score,
                    rotations=rotations,
                    age=age,
                    gender=gender,
                    gender_score=gender_score,
                )


if __name__ == "__main__":
    client = FaceRecognitionClient()
    for i in range(10):
        output = client.listen(FaceRecognitionClient.summarize_times)
        print(output)
        print(output.emotion)
        print(output["emotion"])

    for _ in range(3):
        print(client.listen(FaceRecognitionClient.summarize_timestamps))

    client.close()
