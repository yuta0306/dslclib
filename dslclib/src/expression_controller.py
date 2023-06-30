from dataclasses import dataclass
from typing import Optional

from dslclib.src.base import BaseClient


@dataclass
class ExpressionType:
    """Expression

    Ericaの表情を事前定義したデータクラス．
    ExpressionType()とインスタンス化する必要はない．
    """

    MouthA: str = "mouth-a"
    MouthI: str = "mouth-i"
    MouthU: str = "mouth-u"
    MouthE: str = "mouth-e"
    MouthO: str = "mouth-o"
    Normal: str = "normal"
    FullSmile: str = "fullsmile"
    Smile: str = "smile"
    Bad: str = "bad"
    Angry: str = "angry"
    EyeClose: str = "eye-close"
    EyeOpen: str = "eye-open"
    EyeUp: str = "eye-up"
    EyeDown: str = "eye-down"


"""
MouthA: str, default = 'mouth-a'
    「あ」の口
MouthI: str, default = 'mouth-i'
    「い」の口
MouthU: str, default = 'mouth-u'
    「う」の口
MouthE: str, default = 'mouth-e'
    「え」の口
MouthO: str, default = 'mouth-o'
    「お」の口
Normal: str, default = 'normal'
    平常
FullSmile: str, default = 'fullsmile'
    満面の笑顔
Smile: str, default = 'smile'
    笑顔
Bad: str, default = 'bad'
    困った顔
Angry: str, default = 'angry'
    怒った顔
EyeClose: str, default = 'eye-close'
    目を閉じる
EyeOpen: str, default = 'eye-open'
    目を開ける
EyeUp: str, default = 'eye-up'
    上を向く
EyeDown: str, default = 'eye-down'
    下を向く
"""


class ExpressionController(BaseClient):
    """ExpressionController

    Ericaの表情をコントロールするクライアント．
    ソケットにコマンドを送ることでEricaの表情を動かす．
    """

    def __init__(self, ip: Optional[str] = None, port: int = 20000) -> None:
        """
        Parameters
        ----------
        ip: str, optional
            ipアドレス．

            デフォルトはNoneであり，Noneが与えられた時，127.0.0.1(ローカルホスト)を指定し，
            もし，docker内でこのモジュールが立ち上がっていた場合，自動でそれが認識され，host.docker.internalを指定する．

            host.docker.internalは，docker内からローカルホストのポートに接続するために必要である．
        port: int = 20000
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
            port = 20000
        )
        >>>
        """
        super().__init__(ip, port)

    def express(
        self,
        expression: Optional[str] = None,
        valence: float = 0,
        arousal: float = 0,
        dominance: float = 0,
        real_intension: Optional[float] = None,
    ) -> None:
        """
        Ericaの表情を支持するメソッド．
        ExpressionTypeを用いることで，簡単に指示を行うことができる．

        ExpressionTypeに事前定義されたビルトインの表情を指示する場合は，expressionに表情のidを与える．

        独自の表情を指示する場合は，valence, arousal, dominance, real_intensionを与える．

        Parameters
        ----------
        expression: str, optional
            ビルトインの表情を指示する場合に入力する．
            ExpressionTypeを用いることで，簡単にビルトインの表情を指示することができる．
        valence: float, default = 0
            ExpressionTypeにない独自の表情を指示する時に与える．
        arousal: float, default = 0
            ExpressionTypeにない独自の表情を指示する時に与える．
        dominance: float, default = 0
            ExpressionTypeにない独自の表情を指示する時に与える．
        real_intension: float, optional
            ExpressionTypeにない独自の表情を指示する時に与える．
        """
        param_list = list()

        if expression is None:
            param_list.extend(
                [
                    f"valence {valence}",
                    f"arousal {arousal}",
                    f"dominance {dominance}",
                ]
            )
            if real_intension is not None:
                param_list.append(f"realIntention {real_intension}")
        elif expression == "smile":
            param_list.extend(
                [
                    "valence 0.3",
                    "arousal 0.2",
                    "dominance 0.1",
                ]
            )
        elif expression == "normal":
            param_list.extend(
                [
                    "valence 0",
                    "arousal 0",
                    "dominance 0",
                    "realIntention 0",
                ]
            )

        if len(param_list) > 0:
            param_list.append("expression MoodBasedFACS")
            command = "\n".join(param_list) + "\n"
            self.sock.send(command.encode())
            return
        command = f"expression {expression}\n"
        self.sock.send(command.encode())


if __name__ == "__main__":
    import time

    controller = ExpressionController()
    controller.express(ExpressionType.FullSmile)
    time.sleep(3)
    controller.express(ExpressionType.Smile)
    time.sleep(3)
    controller.express(valence=0.2, arousal=0.8, dominance=0.4)
    controller.close()