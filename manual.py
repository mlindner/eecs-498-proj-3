from time import sleep
from joy import *

class Controller( JoyApp ):
    MOTOR_LEFT_BOTTOM = 0
    MOTOR_LEFT_TOP = 1
    MOTOR_RIGHT_BOTTOM = 3
    MOTOR_RIGHT_TOP = 2

    # Events names generated from the concatenation of event kind + event index
    # The format is:
    # 'eventname': (sensor_max_value, motor_number)
    events = {
        'slider1': (127, MOTOR_LEFT_BOTTOM),
        'slider2': (127, MOTOR_LEFT_TOP),
        'slider3': (127, MOTOR_RIGHT_BOTTOM),
        'slider4': (127, MOTOR_RIGHT_TOP),
    }

    # Stored values for all event types to be summed for resultant motor speed
    values = [
        {key: 0 for key in events},
        {key: 0 for key in events},
    ]

    def __init__(self, spec, *arg, **kw):
        JoyApp.__init__(self, *arg, **kw)
        self.spec = spec

    def onStart(self):
        self.output = self.setterOf(self.spec)

        motor_items = self.robot.items()
        self.motors = [ motor[1] for motor in motor_items ]

        for motor in self.motors:
            motor.set_mode(0)
            # Set min angle = 0
            motor.pna.mem_write_fast(motor.mcu.cw_angle_limit, 0)
            # Set max angle = 1023
            motor.pna.mem_write_fast(motor.mcu.ccw_angle_limit, 1023)

    def onEvent(self, evt):
        # We only care about midi events right now
        if evt.type == MIDIEVENT:
            # Generate event name
            kind = evt.kind + str(evt.index)
            # Try in case we got an event we havent set
            try:
                print(kind)
                print(self.events[kind])
                params = self.events[kind]
            except KeyError:
                return JoyApp.onEvent(self, evt)

            # Computation the new motor input
            position = (evt.value * 1023) / params[0]

            # Set motor position
            motor = self.motors[params[1]]
            motor.pna.mem_write_fast(motor.mcu.goal_position, position)

if __name__ == '__main__':
    app = Controller("#output ", robot=dict(count=4))
    app.run()
