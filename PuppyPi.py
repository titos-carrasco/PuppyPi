import roslibpy  # pip install roslibpy
from typing import Tuple
import math
import time


class PuppyPi:
    # acciones predefinidas
    ACTION_BOXING = "boxing"
    ACTION_BOXING_2 = "boxing2"
    ACTION_BOW = "bow"
    ACTION_JUMP = "jump"
    ACTION_KICK_BALL_LEFT = "kick_ball_left"
    ACTION_KICK_BALL_RIGHT = "kick_ball_right"
    ACTION_LIE_DOWN = "lie_down"
    ACTION_MONNWALK = "moonwalk"
    ACTION_NOD = "nod"
    ACTION_PEE = "pee"
    ACTION_PUSH_UP = "push-up"
    ACTION_SHAKE_HANDS = "shake_hands"
    ACTION_SHAKE_HEAD = "shake_head"
    ACTION_SIT = "sit"
    ACTION_SPACEWALK = "spacewalk"
    ACTION_STRETCH = "stretch"
    ACTION_STAND_2_LEGS = "2_legs_stand"
    ACTION_STAND_4_LEGS = "stand"
    ACTION_UP_STAIRS_2CM = "up_stairs_2cm"
    ACTION_UP_STAIRS_3_5CM = "up_stairs_3.5cm"
    ACTION_UP_STAIRS_3_5CM_0 = "up_stairs_3.5cm0"
    ACTION_UP_STAIRS_3_5CM_1 = "up_stairs_3.5cm1"
    ACTION_WAVE = "wave"

    # tipos de pasos predefinidos
    GAIL_TROT = "Trot"
    GAIL_AMBLE = "Amble"
    GAIL_WALK = "Walk"

    def __init__(self, ip: str):
        """Establece la conexion con el robot dado por la direccion IP.

        Args:
            ip (str): direccion IP del robot.
        """
        # nos conectamos
        self.ros = roslibpy.Ros(host=ip, port=9090)
        self.ros.run()

        # para las acciones predefinidas
        service = "/puppy_control/runActionGroup"
        msg_type = self.ros.get_topic_type(service)
        self.action_group_srv = roslibpy.Service(self.ros, service, msg_type)

        # para desplazamiento
        topic = "/puppy_control/velocity"
        msg_type = self.ros.get_topic_type(topic)
        self.velocity_pub = roslibpy.Topic(self.ros, topic, msg_type, queue_size=1)

        # para capturar la camara
        topic = "/usb_cam/image_raw"
        msg_type = self.ros.get_topic_type(topic)
        self.image_raw_pub = roslibpy.Topic(self.ros, topic, msg_type, queue_length=1)

        # para las posturas
        topic = "/puppy_control/pose"
        msg_type = self.ros.get_topic_type(topic)
        self.pose_pub = roslibpy.Topic(self.ros, topic, msg_type, queue_size=1)
        self.pose_params = {}

        # para las formas de desplazamiento
        topic = "/puppy_control/gait"
        msg_type = self.ros.get_topic_type(topic)
        self.gait_pub = roslibpy.Topic(self.ros, topic, msg_type, queue_size=1)

        # dejamos en posicion de pie al robot
        self.setPoseStand()

    def finish(self) -> None:
        """Finaliza la interaccion con el robot."""
        self.gait_pub.unsubscribe()
        self.pose_pub.unsubscribe()
        self.image_raw_pub.unsubscribe()
        self.velocity_pub.unadvertise()
        self.action_group_srv.unadvertise()
        self.ros.terminate()

    def runActionGroup(self, action: str, pause: float = 4.0) -> None:
        """Ejecuta una de las acciones predefinidas del robot.

        Args:
            action (str): la accion a ejecutar.
            pause (float, optional): tiempo en segundos de pausa antes de retornar. Por defecto es 4.0s.
        """
        request = roslibpy.ServiceRequest({"name": action + ".d6ac"})
        self.action_group_srv.call(request)

        # no sabemos cuando el servicio ha finalizado su ejecucion
        time.sleep(pause)

    def move(self, x: float, yaw_rate: float, gait: str = "Walk") -> None:
        """Inicia el desplazamiento del robot.

        Args:
            x (float): mueve el robot hacia atras o hacia adelante (-35 a +35 ¿mm/s?).
            yaw_rate (float): mueve el robot hacia la izquierda o hacia la derecha (-50 a +50 grados/s).
            gait (str, optional): la forma de andar del robot (default GAIL_WALK).
        """
        # preparamos paranetros segun el modo de andar
        if gait == PuppyPi.GAIL_TROT:
            gait_config = {
                "overlap_time": 0.2,
                "swing_time": 0.3,
                "clearance_time": 0.0,
                "z_clearance": 5,
            }
            self.pose_params["x_shift"] = -0.6
        elif gait == PuppyPi.GAIL_AMBLE:
            gait_config = {
                "overlap_time": 0.1,
                "swing_time": 0.2,
                "clearance_time": 0.1,
                "z_clearance": 5,
            }
            self.pose_params["x_shift"] = -0.9
        else:  # GAIL_WALK
            gait_config = {
                "overlap_time": 0.1,
                "swing_time": 0.2,
                "clearance_time": 0.3,
                "z_clearance": 5,
            }
            self.pose_params["x_shift"] = -0.65

        # la postura
        self.pose_pub.publish(roslibpy.Message(self.pose_params))

        # la forma de andar
        self.gait_pub.publish(roslibpy.Message(gait_config))

        # lo ponemos en marcha
        self.velocity_pub.publish(
            roslibpy.Message({"x": x, "y": 0.0, "yaw_rate": math.radians(-yaw_rate)})
        )

    def move_stop(self) -> None:
        """Detiene el desplazamiento del robot"""
        self.velocity_pub.publish(
            roslibpy.Message({"x": 0.0, "y": 0.0, "yaw_rate": 0.0})
        )

    def imageRaw_start(self, callback) -> None:
        """Inicia la captura de imagenes desde la camara del robot.

        La funcion callback recibira un parametro ('result')  del tipo diccionario

        Args:
            callback (function): funcion a ser invocada cada vez que se tenga una imagen de la camara.

        Examples:
            Ejemplo dentro del callback para opencv:

                def callback(result):
                    h = result["height"]
                    w = result["width"]
                    enc = result["encoding"]
                    img = result["data"].encode("ascii")
                    img = base64.b64decode(img)
                    img = np.frombuffer(img, np.uint8)
                    img = img.reshape((h, w, 3))
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


        """
        self.image_raw_pub.subscribe(callback)

    def imageRaw_stop(self) -> None:
        """Finaliza la captura de imagenes desde la camara del robot."""
        self.image_raw_pub.unsubscribe()

    def setPose(
        self, roll: float, pitch: float, height: float, run_time: float = 1.0
    ) -> None:
        """Establece una postura para el robot.

        Args:
            roll (float): -30 a 30 grados.
            pitch (float): -30 a 30 grados.
            height (float): altura de las patas del robot (50 a 150 mm).
            run_time (float, optional): tiempo de ejecucion para alcanzar la postura. Por defecto en 1.0s.
        """
        self.pose_params = {
            "roll": math.radians(roll),
            "pitch": math.radians(pitch),
            "yaw": 0.0,
            "height": -height / 10.0,
            "x_shift": 0.0,
            "stance_x": 0.0,
            "stance_y": 0.0,
            "run_time": int(run_time * 1000.0),  # debe ser integer
        }
        self.pose_pub.publish(roslibpy.Message(self.pose_params))
        time.sleep(run_time + 0.2)

    def setPoseStand(self, run_time: float = 1.0) -> None:
        """Establece la postura de pie para el robot.

        Args:
            run_time (float, optional): tiempo de ejecucion para alcanzar la postura. Por defecto en 1.0s.
        """
        self.pose_params = {
            "roll": 0.00,
            "pitch": 0.00,
            "yaw": 0.00,
            "height": -10.0,
            "x_shift": -0.5,
            "stance_x": 0.0,
            "stance_y": 0.0,
            "run_time": int(run_time * 1000.0),  # debe ser integer
        }
        self.pose_pub.publish(roslibpy.Message(self.pose_params))
        time.sleep(run_time + 0.2)

    def setPoseLieDown(self, run_time: float = 1.0) -> None:
        """Establece la postura agachado para el robot.

        Args:
            run_time (float, optional): tiempo de ejecucion para alcanzar la postura. Por defecto en 1.0s.
        """
        self.pose_params = {
            "roll": 0.00,
            "pitch": 0.00,
            "yaw": 0.00,
            "height": -5.0,
            "x_shift": 2.0,
            "stance_x": 0.0,
            "stance_y": 0.0,
            "run_time": int(run_time * 1000.0),  # debe ser integer
        }
        self.pose_pub.publish(roslibpy.Message(self.pose_params))
        time.sleep(run_time + 0.2)
