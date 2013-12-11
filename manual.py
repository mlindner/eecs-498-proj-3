from time import sleep
from joy import *

class Controller( JoyApp ):

    # Mapping motor positions to numeric values
    MOTOR_LEFT_FRONT = 3
    MOTOR_LEFT_BACK = 1
    MOTOR_RIGHT_FRONT = 0
    MOTOR_RIGHT_BACK = 2

    # Max and min angles motors allowed to rotate through
    MIN_ANGLE = 196
    MAX_ANGLE = 826
    ANGLE_RANGE = MAX_ANGLE - MIN_ANGLE

    # tip motors 185
    # back motors 290
    # tip motors 511
    # back motors 511
    # repeat
    gait = [[0, 185], [1, 290], [0, 511], [1,511]]
    current_gait_left = 0
    current_gait_right = 0
    left_delay = 100000
    right_delay = 100000
    last_event_left = 0
    last_event_right = 0


    # Events names generated from the concatenation of event kind + event index
    # The format is:
    # 'eventname': (sensor_max_value, motor_location)
    events = {
        'slider1': (127, (MOTOR_LEFT_FRONT, MOTOR_LEFT_BACK)),
        'slider2': (127, (MOTOR_RIGHT_FRONT, MOTOR_RIGHT_BACK)),
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
            motor.pna.mem_write_fast(motor.mcu.goal_position, 511)

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

            delay = (params[0] - evt.value) * 100000 / params[0]
            if kind == 'slider1':
                self.left_delay = delay
            if kind == 'slider2':
                self.right_delay = delay

            # Computation of event time
            #position = (evt.value * self.ANGLE_RANGE) / params[0] + self.MIN_ANGLE

            # Set motor position
            #motor = self.motors[params[1]]
            #motor.pna.mem_write_fast(motor.mcu.goal_position, position)
        else:
            if self.now + self.left_delay > self.last_event_left:
                gait_elem = self.gait[current_gait_left]
                motor_num = self.events['slider1'][1][gait_elem[0]]
                motor = self.motors[motor_num]
                motor.pna.mem_write_fast(motor.mcu.goal_position, gait_elem[1])
                current_gait_left = current_gait_left + 1
                self.last_event_left = self.now

            if self.now + self.right_delay > self.last_event_right:
                gait_elem = self.gait[current_gait_right]
                motor_num = self.events['slider2'][1][gait_elem[0]]
                motor = self.motors[motor_num]
                motor.pna.mem_write_fast(motor.mcu.goal_position, gait_elem[1])
                current_gait_right = current_gait_right + 1
                self.last_event_right = self.now
                
            
            

if __name__ == '__main__':
    app = Controller("#output ", robot=dict(count=4))
    app.run()
