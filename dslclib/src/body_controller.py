import json
from dataclasses import dataclass
from typing import Literal, Optional

from dslclib.src.base import BaseClient


@dataclass
class MotionType:
    """MotinonType
    Ericaのモーションの命令を一部事前定義している．
    MotionType()とインスタンス化する必要はない．

    ここでは，Default, Greeting, Nono, NodDeep, Nod, RightHandBasePosition, LeftHandBasePositionを用意している．

    以下のプロパティ以外は、Erica@CGのMotionを参照されたい．
    CGEricaの画面の左上のウィンドウに全てのモーションの命令が書かれている．

    Examples
    --------
    >>> MotionType.Default
    DefaultMotion
    >>> MotionType.Nod
    nod
    >>> MotionType.RightHandBasePosition
    righthandbaseposition
    """

    Default: Literal["DefaultMotion"] = "DefaultMotion"
    Greeting: Literal["greeting"] = "greeting"
    Nono: Literal["nono"] = "nono"
    NodDeep: Literal["nod_deep"] = "nod_deep"
    Nod: Literal["nod"] = "nod"
    RightHandBasePosition: Literal["righthandbaseposition"] = "righthandbaseposition"
    LeftHandBasePositin: Literal["lefthandbaseposition"] = "lefthandbaseposition"


"""
Default: str, default = "DefaultMotion"
    デフォルトの姿勢にする
Greeting: str, default = "greeting"
    挨拶をする．軽い会釈をする．
Nono: str, default = "nono"
    ノーノー．首を振る．
NodDeep: str, default = "nod_deep"
    深く頷く
Nod: str, default = "nod"
    頷く
RightHandBasePosition: str, default = "righthandbaseposition"
    右手を基準の場所に戻す
LeftHandBasePosition: str, default = "lefthandbaseposition"
    左手を基準の場所に戻す
"""


@dataclass
class GazeDirection:
    """GazeDirection
    Ericaの目線の方向を事前定義したデータクラス．
    GazeDirection()とインスタンス化する必要はない．

    FrontとRightとLeftを用意している．
    この3方向以外の向きを指定する場合，BodyController.gazeに直接数値を入力することができる．

    Examples
    --------
    >>> GazeDirection.Front
    (0.0, 1.2, 1.5)
    >>> GazeDirection.Right
    (1.0, 1.2, 1.5)
    >>> GazeDirection.Left
    (-1.0, 1.2, 1.5)
    """

    Front: tuple[float, float, float] = (0.0, 1.2, 1.5)
    Right: tuple[float, float, float] = (1.0, 1.2, 1.5)
    Left: tuple[float, float, float] = (-1.0, 1.2, 1.5)


@dataclass
class GazeObject:
    """GazeObject

    Ericaの目線の対象を事前定義したデータクラス．
    GazeObject()とインスタンス化する必要はない．

    Desk，Monitor，Sofaを用意している．

    Examples
    --------
    >>> GazeObject.Monitor
    monitor
    >>> GazeObject.Desk
    desk
    >>> GazeObject.Sofa
    Sofa
    """

    Monitor: Literal["monitor"] = "monitor"
    Desk: Literal["desk"] = "desk"
    Sofa: Literal["Sofa"] = "Sofa"


"""
Monitor: str, default = "monitor"
    Ericaの目線をモニターに向ける
Desk: str, default = "desk"
    Ericaの目線をデスクに向ける
Sofa: str, default = "Sofa"
    Ericaの目線をソファに向ける
"""


@dataclass
class ControllerType:
    """ControllerType

    Ericaのどの部分をコントロールするかを指定するデータクラス．
    ControllerType()とインスタンス化する必要はない．

    EyeControllerはEricaの目線のコントロールを指定し，HeadControllerはEricaの頭の向きのコントロールを指定する．
    指定する文字列が長いため，このデータクラスを使うことを推奨する．

    Examples
    --------
    >>> ControllerType.Eye
    EyeController
    >>> ControllerType.Head
    HeadController
    """

    Eye: Literal["EyeController"] = "EyeController"
    Head: Literal["HeadController"] = "HeadController"


"""
Eye: str, default = "EyeController"
    目線を動かすことを指示
Head: str, default = "HeadController"
    顔の向きを動かすことを指示
"""


class BodyController(BaseClient):
    """BodyController

    Ericaの身体をコントロールするクライアント．
    ソケットにコマンドを送ることでEricaを動かす．
    """

    def __init__(self, ip: Optional[str] = None, port: int = 21000) -> None:
        """
        Parameters
        ----------
        ip: str, optional
            ipアドレス．

            デフォルトはNoneであり，Noneが与えられた時，127.0.0.1(ローカルホスト)を指定し，
            もし，docker内でこのモジュールが立ち上がっていた場合，自動でそれが認識され，host.docker.internalを指定する．

            host.docker.internalは，docker内からローカルホストのポートに接続するために必要である．
        port: int = 21000
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
            port = 21000
        )
        >>>
        """
        super().__init__(ip, port)

    def play_motion(self, motion: str) -> None:
        """
        モーション名に対応するモーションをEricaに指示するメソッド

        Parameters
        ----------
        motion: str
            モーション名．MotionTypeのデータクラスを使うことで，簡単に指示を行うことができる．
            MotionTypeでサポートしていないモーション名もたくさんあり，これらはCGEricaの画面左上で確認することができる．
            より詳細なモーションを指示したい場合は，直接strを引数に与えること．

        Returns
        -------

        Examples
        --------
        >>> client.play_motion(MotionType.Greeting)
        >>> client.play_motion(motion=MotionType.Greeting)
        >>> client.play_motion("greeting")
        >>>
        """
        command = f"playmotion={motion}\n"
        self.sock.send(command.encode())

    def gaze(
        self,
        obj: Optional[str] = None,
        direction: Optional[tuple[float, float, float]] = None,
        eye: Optional[tuple[float, float, float]] = None,
        head: Optional[tuple[float, float, float]] = None,
    ) -> None:
        """
        Ericaの目線または顔の向きを指示するメソッド．
        GazeObject，GazeDirectionを用いることで，簡単に指示を行うことができる．

        obj, direction, eye, headのいずれかは引数として入力しなければならない．

        目線と顔の向きの両方を，同じ向きに動かす場合はdirectionに座標を与える．

        目線のみならばeye，顔の向きのみならばheadに座標を与える．

        また，目線と顔の向きを動かすが，別の座標をそれぞれ指示したい場合は，eyeとheadにそれぞれ座標を与える．

        Parameters
        ----------
        obj: str, optional
            見るオブジェクトの名前．指定したオブジェクトの方向に目線と顔を向ける．
            ここではデータクラスGazeObjectを用いることができる．
            直接文字列を与えることも可能．
        direction: tuple, optional
            指定した座標に対して目線と顔を向ける．
            ここではデータクラスGazeDirectionを用いることができる．
            直接座標をタプルで与えることも可能．
        eye: tuple, optional
            指定した座標に対して目線のみを向ける．
            ここではデータクラスGazeDirectionを用いることができる．
            直接座標をタプルで与えることも可能．
        head: tuple, optional
            指定した座標に対して顔のみを向ける．
            ここではデータクラスGazeDirectionを用いることができる．
            直接座標をタプルで与えることも可能．

        Returns
        -------

        Examples
        --------
        >>> client.gaze(obj=GazeObject.Sofa)
        >>> client.gaze(direction=GazeDirection.Right)  # 目線と顔の向きを右に
        >>> client.gaze(eye=GazeDirection.Right)  # 目線のみを右に
        >>> client.gaze(eye=GazeDirection.Right, head=(0.0, 1.0, 2.0))  # 目線と顔の向きを別にできる．また，座標を直接与えられる．
        >>> client.gaze()  # 何も引数を与えないとエラー
        ValueError("いずれかの引数に正しい引数を入力してください。")
        """
        if obj is None and direction is None and eye is None and head is None:
            raise ValueError("いずれかの引数に正しい引数を入力してください。")

        if obj is not None:
            self.sock.send(
                self._create_command(
                    controller=ControllerType.Eye,
                    obj=obj,
                    direction=(0, 0, 0),
                ).encode()
            )
            self.sock.send(
                self._create_command(
                    controller=ControllerType.Head,
                    obj=obj,
                    direction=(0, 0, 0),
                ).encode()
            )

        if direction is not None:
            self.sock.send(
                self._create_command(
                    controller=ControllerType.Eye,
                    obj="",
                    direction=direction,
                ).encode()
            )
            self.sock.send(
                self._create_command(
                    controller=ControllerType.Head,
                    obj="",
                    direction=direction,
                ).encode()
            )

        if eye is not None:
            self.sock.send(
                self._create_command(
                    controller=ControllerType.Eye,
                    obj="",
                    direction=eye,
                ).encode()
            )

        if head is not None:
            self.sock.send(
                self._create_command(
                    controller=ControllerType.Head,
                    obj="",
                    direction=head,
                ).encode()
            )

    def _create_command(
        self,
        controller: str,
        obj: str,
        direction: tuple[float, float, float],
    ) -> str:
        cmd = {
            "id": controller,
            "motionTowardObject": obj,
            "targetMotionMode": 2,
            "targetPoint": {"x": direction[0], "y": direction[1], "z": direction[2]},
            "translateSpeed": 2.0,
        }
        return f"{controller}={json.dumps(cmd)}\n"


if __name__ == "__main__":
    import time

    controller = BodyController()

    controller.play_motion(MotionType.Greeting)
    time.sleep(2)
    controller.play_motion(MotionType.Nono)
    time.sleep(2)

    controller.gaze(GazeObject.Monitor)
    time.sleep(3)
    controller.gaze(direction=GazeDirection.Left)
    controller.gaze(direction=GazeDirection.Front)
    time.sleep(3)

    controller.gaze(eye=GazeDirection.Front, head=GazeDirection.Right)

    controller.close()
