import multi_half_bridge_py as mhb
from time import sleep
"""
print("[INFO] Starte Infineon TLE94112 Test...")

# Create a Tle94112Rpi instance for each motor controller
controller_1 = mhb.Tle94112Rpi()
controller_2 = mhb.Tle94112Rpi()
controller_3 = mhb.Tle94112Rpi()

# Create a Tle94112Motor instance for each connected load
motor_1 = mhb.Tle94112Motor(controller_1)
motor_2 = mhb.Tle94112Motor(controller_2)
motor_3 = mhb.Tle94112Motor(controller_3)

print("[INFO] Initialisiere Controller und bereinige Fehler...")
controller_1.begin()
controller_1.clearErrors()

#Mund, Kopf, Flosse
#0, 1, 0
motor_1.connect(motor_1.LOWSIDE, controller_1.TLE_HB6)
motor_1.setPwm(motor_1.LOWSIDE, controller_1.TLE_NOPWM)
motor_1.setPwm(motor_1.HIGHSIDE, controller_1.TLE_PWM1)

motor_1.begin()

print("[OK] Schalte Ausg  nge HB5 und HB6 EIN (Spannung liegt an)!")
motor_1.start(200)

print("[WAIT] Warte 3 Sekunden...")
sleep(3)

print("[OK] Schalte Ausg  nge AUS (Floating). Test beendet.")
motor_1.coast()

sleep(1)

print("---------Zweiter Start-----------")

controller_2.begin()
controller_2.clearErrors()

#0, 0, 1
motor_2.connect(motor_2.HIGHSIDE, controller_2.TLE_HB6)
motor_2.connect(motor_2.LOWSIDE, controller_2.TLE_HB5)
motor_2.setPwm(motor_2.LOWSIDE, controller_2.TLE_NOPWM)
motor_2.setPwm(motor_2.HIGHSIDE, controller_2.TLE_PWM1)

motor_2.begin()

print("HB6 + HB5")
motor_2.start(200)

print("------ Motor hat gestartet --------")
sleep(3)

print("------ Schalte aus -------")
motor_2.coast()

print("-------- Dritter Start---------")

controller_3.begin()
controller_3.clearErrors()

#1, 0, 0
motor_3.connect(motor_3.HIGHSIDE, controller_3.TLE_HB9)
motor_3.connect(motor_3.LOWSIDE, controller_3.TLE_HB7)
motor_3.setPwm(motor_3.LOWSIDE, controller_3.TLE_NOPWM)
motor_3.setPwm(motor_3.HIGHSIDE, controller_3.TLE_PWM1)

motor_3.begin()

print(" HB7 + HB9")
motor_3.start(255)

print("------ Motor hat gestartet --------")
sleep(3)

print("------ Schalte aus -------")
motor_3.coast()
"""

class FishController:

    def __init__(self):
        print("[INFO] Starte Infineon TLE94112 Test...")

        # duration constant for movement tests:
        self.duration = 1

        # Create a Tle94112Rpi instance for each motor controller
        self.controller_1 = mhb.Tle94112Rpi()
        self.controller_2 = mhb.Tle94112Rpi()
        self.controller_3 = mhb.Tle94112Rpi()

        # Create a Tle94112Motor instance for each connected load
        self.motor_1 = mhb.Tle94112Motor(self.controller_1)
        self.motor_2 = mhb.Tle94112Motor(self.controller_2)
        self.motor_3 = mhb.Tle94112Motor(self.controller_3)

    def start(self):
        pass

    def stop(self):
        pass

    def move_head(self):

        print("[INFO] Initialisiere Controller_1 und bereinige Fehler...")
        self.controller_1.begin()
        self.controller_1.clearErrors()

        #Mund, Kopf, Flosse
        #0, 1, 0
        self.motor_1.connect(self.motor_1.HIGHSIDE, self.controller_1.TLE_HB5)
        self.motor_1.connect(self.motor_1.LOWSIDE, self.controller_1.TLE_HB6)
        self.motor_1.setPwm(self.motor_1.LOWSIDE, self.controller_1.TLE_NOPWM)
        self.motor_1.setPwm(self.motor_1.HIGHSIDE, self.controller_1.TLE_PWM1)

        self.motor_1.begin()

        print("[OK] Schalte Ausg  nge HB5 und HB6 EIN (Spannung liegt an)!")
        self.motor_1.start(200)

        print("[WAIT] Warte x Sekunden...")
        sleep(self.duration)

        print("[OK] Schalte Ausg  nge AUS (Floating). Test beendet.")
        self.motor_1.coast()

        sleep(1)

    def move_tail(self):
        print("---------Zweiter Start-----------")

        self.controller_2.begin()
        self.controller_2.clearErrors()

        #0, 0, 1
        self.motor_2.connect(self.motor_2.HIGHSIDE, self.controller_2.TLE_HB6)
        self.motor_2.connect(self.motor_2.LOWSIDE, self.controller_2.TLE_HB5)
        self.motor_2.setPwm(self.motor_2.LOWSIDE, self.controller_2.TLE_NOPWM)
        self.motor_2.setPwm(self.motor_2.HIGHSIDE, self.controller_2.TLE_PWM1)

        self.motor_2.begin()

        print("HB6 + HB5")
        self.motor_2.start(200)

        print("------ Motor hat gestartet --------")
        sleep(self.duration)

        print("------ Schalte aus -------")
        self.motor_2.coast()

    def mouth_action(self):
        print("-------- Dritter Start---------")

        self.controller_3.begin()
        self.controller_3.clearErrors()

        #1, 0, 0
        self.motor_3.connect(self.motor_3.HIGHSIDE, self.controller_3.TLE_HB9)
        self.motor_3.connect(self.motor_3.LOWSIDE, self.controller_3.TLE_HB7)
        self.motor_3.setPwm(self.motor_3.LOWSIDE, self.controller_3.TLE_NOPWM)
        self.motor_3.setPwm(self.motor_3.HIGHSIDE, self.controller_3.TLE_PWM1)

        self.motor_3.begin()

        print(" HB7 + HB9")
        self.motor_3.start(255)

        print("------ Motor hat gestartet --------")
        sleep(self.duration)

        print("------ Schalte aus -------")
        self.motor_3.coast()



if __name__ == '__main__':
    fish = FishController()

    fish.mouth_action()
    fish.move_head()
    fish.move_tail()