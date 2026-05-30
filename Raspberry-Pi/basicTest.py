import multi_half_bridge_py as mhb
from time import sleep

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