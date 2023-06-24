from dslclib.src.base import BaseClient
import json
from dataclasses import dataclass
from typing import Literal


@dataclass
class MotionType:
    """MotinonType
    以下のプロパティ以下は、Erica@CGのMotionを参照してください。
    """
    default: str = "DefaultMotion"
    Greeting: str = "greeting"
    Nono: str = "nono"
    NodDeep: str = "nod_deep"
    Nod: str = "nod"
    RightHandBasePosition: str = "righthandbaseposition"
    LeftHandBasePositin: str = "lefthandbaseposition"


@dataclass
class GazeDirection:
    Front: tuple[int, int, int] = (0.0, 1.2, 1.5)
    Right: tuple[int, int, int] = (1.0, 1.2, 1.5)
    Left: tuple[int, int, int] = (-1.0, 1.2, 1.5)


@dataclass
class GazeObject:
    Monitor: str = "monitor"
    Desk: str = "desk"
    Sofa: str = "Sofa"


@dataclass
class ControllerType:
    Eye: str = "EyeController"
    Head: str = "HeadController"


class BodyController(BaseClient):
    """BodyController

    Attributes
    ----------
    ip: str
    port: int
    sock: socket.socket
    """
    def __init__(self, ip: str | None = None, port: int = 21000) -> None:
        super().__init__(ip, port)

    def play_motion(
            self,
            motion: Literal[
                "greeting",
                "nono",
                "nod_deep",
                "nod",
            ],
        ) -> None:
        """
        Parameters
        ----------
        motion: str
        """
        command = f"playmotion={motion}\n"
        self.sock.send(command.encode())

    def gaze(
        self,
        obj: Literal["monitor", "desk", "Sofa"] | None = None,
        direction: tuple[int, int, int] | None = None,
        eye: tuple[int, int, int] | None = None,
        head: tuple[int, int, int] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        obj: str, optional
            見るオブジェクトの名前。指定したオブジェクトの方向に目線と顔を向ける。
        direction: tuple, optional
            指定した座標に対して目線と顔を向ける。
        eye: tuple, optional
            指定した座標に対して目線のみを向ける。
        head: tuple, optional
            指定した座標に対して顔のみを向ける。
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
        direction: tuple[int, int, int]
    ) -> str:
        cmd = {
            "id": controller,
            "motionTowardObject": obj,
            "targetMotionMode": 2,
            "targetPoint": {"x": direction[0],"y": direction[1],"z": direction[2]},
            "translateSpeed": 2.0
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
