from time import sleep
from joy import *

class Controller( JoyApp ):

    # Mapping motor positions to numeric values
    MOTOR_LEFT_FRONT = 3
    MOTOR_LEFT_BACK = 0
    MOTOR_RIGHT_FRONT = 1
    MOTOR_RIGHT_BACK = 2

    # Max and min angles motors allowed to rotate through
    MIN_ANGLE = 196
    MAX_ANGLE = 826
    ANGLE_RANGE = MAX_ANGLE - MIN_ANGLE

    # tip motors 185


    # Events names generated from the concatenation of event kind + event index
    # The format is:
    # 'eventname': (sensor_max_value, motor_location)
    events = {
        'slider1': (127, MOTOR_LEFT_FRONT),
        'slider2': (127, MOTOR_LEFT_BACK),
        'slider3': (127, MOTOR_RIGHT_BACK),
        'slider4': (127, MOTOR_RIGHT_FRONT),
    }

    def __init__(self, spec, *arg, **kw):
        JoyApp.__init__(self, *arg, **kw)
        self.spec = spec

    def onStart(self):
        self.output = self.setterOf(self.spec)

        motor_items = self.robot.items()
        self.motors = [ motor[1] for motor in motor_items ]

        for motor in self.motors:
            motor.set_mode(0)
            # Set min and max angle
            motor.pna.mem_write_fast(motor.mcu.cw_angle_limit, self.MIN_ANGLE)
            motor.pna.mem_write_fast(motor.mcu.ccw_angle_limit, self.MAX_ANGLE)

    def onEvent(self, evt):
        # We only care about midi events right now
        if evt.type == MIDIEVENT:
            # Generate event name
            kind = evt.kind + str(evt.index)
            # Try in case we got an event we havent set
            try:
                params = self.events[kind]
            except KeyError:
                return JoyApp.onEvent(self, evt)

            # Computation the new motor input
            position = (evt.value * self.ANGLE_RANGE) / params[0] + self.MIN_ANGLE

            # Set motor position
            motor = self.motors[params[1]]
            motor.pna.mem_write_fast(motor.mcu.goal_position, position)

if __name__ == '__main__':
    app = Controller("#output ", robot=dict(count=4))
    app.run()
