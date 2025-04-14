import tkinter as tk
from tkinter import ttk

from PuppyPi import PuppyPi


class App:
    actions = {
        "Boxing": PuppyPi.ACTION_BOXING,
        "Bow": PuppyPi.ACTION_BOW,
        "Jump": PuppyPi.ACTION_JUMP,
        "Lie Down": PuppyPi.ACTION_LIE_DOWN,
        "Moon Walk": PuppyPi.ACTION_MONNWALK,
        "Nod": PuppyPi.ACTION_NOD,
        "PEE": PuppyPi.ACTION_PEE,
        "Push Up": PuppyPi.ACTION_PUSH_UP,
        "Shake Hands": PuppyPi.ACTION_SHAKE_HANDS,
        "Shake Head": PuppyPi.ACTION_SHAKE_HEAD,
        "Sit": PuppyPi.ACTION_SIT,
        "Space Walk": PuppyPi.ACTION_SPACEWALK,
        "Stretch": PuppyPi.ACTION_STRETCH,
        "Stand 2 Legs": PuppyPi.ACTION_STAND_2_LEGS,
        "Stand 4 Legs": PuppyPi.ACTION_STAND_4_LEGS,
        "Wave": PuppyPi.ACTION_WAVE,
    }

    def __init__(self):
        # acceso al robot
        self.puppy = None

        # la ventana principal
        self.root = tk.Tk()
        self.root.title("Control del Robot PuppyPi")
        self.root.resizable(False, False)
        self.root_width = 800
        self.root_height = 507
        self.root.geometry(f"{self.root_width}x{self.root_height}")

        # el contenedor de todos los objetos
        self.win = tk.Canvas(
            self.root,
            width=self.root_width,
            height=self.root_height,
            bg="white",
            bd=0,
            highlightthickness=0,
        )
        self.win.place(x=0, y=0)

        # la imagen de fondo
        self.fondo_img = tk.PhotoImage(file="./images/TkPuppyPi.png")
        self.fondo = self.win.create_image(0, 0, anchor="nw", image=self.fondo_img)

        # para establecer la velocidad de desplazamiento
        self.scl_velocity = tk.Scale(
            self.win,
            orient=tk.HORIZONTAL,
            from_=0,
            to=35,
            bg="white",
            bd=0,
            highlightthickness=0,
            length=240,
        )
        self.scl_velocity.set(10)
        self.scl_velocity.place(x=110, y=50)

        # para establecer la velocidad de giro
        self.scl_yaw_rate = tk.Scale(
            self.win,
            orient=tk.HORIZONTAL,
            from_=0,
            to=50,
            bg="white",
            bd=0,
            highlightthickness=0,
            length=240,
        )
        self.scl_yaw_rate.set(25)
        self.scl_yaw_rate.place(x=110, y=100)

        # para mostrar el estado de la conexion
        self.lbl_status = tk.Label(
            self.win,
            text="Disconnected",
            font=("Arial", 10, "normal"),
            fg="red",
            bg="white",
        )
        self.lbl_status.place(x=40, y=160)

        # para seleccionar la forma de andar
        self.cbb_gait = ttk.Combobox(
            self.win,
            values=["Amble", "Trot", "Walk"],
            width=8,
            font=("Arial", 10, "normal"),
            state="readonly",
        )
        self.cbb_gait.current(2)
        self.cbb_gait.place(x=300, y=160)

        # para establecer los valores por defecto
        self.btn_reset = tk.Button(
            self.win,
            text="RESET",
            width=40,
            height=1,
            bg="#FFA500",
            fg="white",
            font=("Arial", 10, "normal"),
            relief="flat",
            command=self.doReset,
        )
        self.btn_reset.place(x=40, y=467)

        # para estblecer la altura de las patas
        self.scl_height = tk.Scale(
            self.win,
            orient=tk.HORIZONTAL,
            from_=50,
            to=150,
            bg="white",
            bd=0,
            highlightthickness=0,
            length=260,
        )
        self.scl_height.set(100)
        self.scl_height.place(x=480, y=54)
        self.scl_height.bind("<ButtonRelease-1>", self.doPose)

        # para establecer la inclinacion frontal
        self.scl_pitch = tk.Scale(
            self.win,
            orient=tk.HORIZONTAL,
            from_=-30,
            to=30,
            bg="white",
            bd=0,
            highlightthickness=0,
            length=260,
        )
        self.scl_pitch.set(0)
        self.scl_pitch.place(x=480, y=125)
        self.scl_pitch.bind("<ButtonRelease-1>", self.doPose)

        # para establecer la inclinacion lateral
        self.scl_roll = tk.Scale(
            self.win,
            orient=tk.HORIZONTAL,
            from_=-30,
            to=30,
            bg="white",
            bd=0,
            highlightthickness=0,
            length=260,
        )
        self.scl_roll.set(0)
        self.scl_roll.place(x=480, y=197)
        self.scl_roll.bind("<ButtonRelease-1>", self.doPose)

        # los botones con acciones predefinidas
        x = 420
        y = 320
        for action in App.actions:
            btn = tk.Button(
                self.win,
                text=action,
                width=12,
                height=1,
                font=("Arial", 8, "normal"),
                relief="groove",
                command=lambda act=action: self.doAction(act),
            )
            btn.place(x=x, y=y)
            x = x + 94
            if x > 740:
                x = 420
                y = y + 32

        # la direccion IP del robot
        self.ent_ip = tk.Entry(
            self.win, width=20, font=("Arial", 10, "normal"), justify="center"
        )
        self.ent_ip.insert(0, "192.168.149.1")
        self.ent_ip.place(x=450, y=471)

        # boton para conectarse al robot
        self.btn_connect = tk.Button(
            self.win,
            text="Connect",
            width=8,
            height=1,
            font=("Arial", 10, "normal"),
            relief="flat",
            command=self.doConnect,
        )
        self.btn_connect.place(x=610, y=468)

        # boton para desconectarse del robot
        self.btn_disconnect = tk.Button(
            self.win,
            text="Disconnect",
            width=8,
            height=1,
            font=("Arial", 10, "normal"),
            relief="flat",
            state="disabled",
            command=self.doDisconnect,
        )
        self.btn_disconnect.place(x=694, y=468)

        # un mensaje mientras interacuamos con el robot
        self.lbl_working = tk.Label(
            self.win,
            text="Working ...",
            bg="lightblue",
            fg="darkblue",
            font=("Helvetica", 16, "bold"),
            bd=2,
            relief="ridge",
            padx=20,
            pady=20,
        )
        self.lbl_working.place(x=-350, y=-200)

        # para finalizar la aplicacion de manera correcta
        self.root.protocol("WM_DELETE_WINDOW", self.doFinish)

    # finalizamos la aplicacion
    def doFinish(self):
        self.root.destroy()
        if not self.puppy is None:
            self.puppy.move_stop()
            self.puppy.finish()

    # volvemos los parametros a su valor inicial
    def doReset(self):
        self.scl_velocity.set(10)
        self.scl_yaw_rate.set(25)
        self.cbb_gait.current(2)
        self.scl_height.set(100)
        self.scl_pitch.set(0)
        self.scl_roll.set(0)
        if not self.puppy is None:
            self.puppy.move_stop()
            self.doPose()

    # conectamos con el robot
    def doConnect(self):
        if self.puppy is None:
            self.modoEjecucion()
            ip = self.ent_ip.get()
            try:
                self.puppy = PuppyPi(ip)
            except:
                self.modoNormal()
                return
            self.lbl_status.config(text="Connected", fg="green")
            self.btn_connect.config(state="disabled")
            self.btn_disconnect.config(state="normal")
            self.doPose()
            self.modoNormal()

    # desconectamos del robot
    def doDisconnect(self):
        if not self.puppy is None:
            self.modoEjecucion()
            self.puppy.move_stop()
            self.puppy.finish()
            self.puppy = None
            self.lbl_status.config(text="Disconnected", fg="red")
            self.btn_connect.config(state="normal")
            self.btn_disconnect.config(state="disabled")
            self.modoNormal()

    # enviamos los parametros de postura
    def doPose(self, event=None):
        if not self.puppy is None:
            self.modoEjecucion()
            height = self.scl_height.get()
            pitch = self.scl_pitch.get()
            roll = self.scl_roll.get()
            self.puppy.setPose(height=height, pitch=pitch, roll=roll, run_time=1)
            self.modoNormal()

    # ejecutamois la accion seleccionada
    def doAction(self, action):
        action = App.actions[action]
        if not self.puppy is None:
            self.modoEjecucion()
            self.puppy.runActionGroup(action, pause=4)
            self.modoNormal()

    # modo ejecucion
    def modoEjecucion(self):
        self.lbl_working.place(x=350, y=200)
        self.root.update()

    # modo normal
    def modoNormal(self):
        self.lbl_working.place(x=-350, y=-200)
        self.root.update()

    # entramos en el loop de tkinter
    def run(self):
        self.win.mainloop()


# ---
app = App()
app.run()
