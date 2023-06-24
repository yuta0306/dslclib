from dslclib.src.base import BaseClient
from dataclasses import dataclass
from typing import Literal


@dataclass
class ExpressionType:
    """Expression

    Attributes
    ----------
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


class ExpressionController(BaseClient):
    """ExpressionController

    """
    def __init__(self, ip: str | None = None, port: int = 20000) -> None:
        super().__init__(ip, port)

    def express(
        self,
        expression: Literal[
            "mouth-a",
            "mouth-i",
            "mouth-u",
            "mouth-e",
            "mouth-o",
            "normal",
            "fullsmile",
            "smile",
            "bad",
            "angry",
            "eye-close",
            "eye-open",
            "eye-up",
            "eye-down"] | None = None,
        valence: float = 0,
        arousal: float = 0,
        dominance: float = 0,
        real_intension: float | None = None,
    ) -> None:
        """
        Parameters
        ----------
        expression: str, optional
        valence: float, default = 0
        arousal: float, default = 0
        dominance: float, default = 0
        real_intension: float, optional
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