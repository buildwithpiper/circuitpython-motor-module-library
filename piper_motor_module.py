################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2021 Piper Learning, Inc. and Matthew Matz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
################################################################################

__version__ = "0.9.0"
__repo__ = "https://github.com/buildwithpiper/circuitpython_motor_module_library.git"


# ----------- Constants and Registers -----------
# Device i2c address
MOTOR_MODULE_ADDR = 0x0F

# Register addresses and masks
REG_MODE1 = 0x00
REG_MODE2 = 0x01

REG_PWM = [0x02, 0x03, 0x04, 0x05]
REG_OUTS = 0x14

OUTPUT_OFF  = 0b00000000
OUTPUT_ON   = [0b00000001, 0b00000100, 0b00010000, 0b01000000]
OUTPUT_PWM  = [0b00000010, 0b00001000, 0b00100000, 0b10000000]
OUTPUT_MASK = [0b00000011, 0b00001100, 0b00110000, 0b11000000]

SERVO_ATTACHED = [0x1C, 0x1D]
SERVO_ANGLE = [0x1E, 0x1F]


# ----------- Methods -----------
class piper_motor_module:
  # Initialize the sensor
  def __init__(self, i2c, address=MOTOR_MODULE_ADDR):

    self.i2c = i2c
    self.address = address

    while not self.i2c.try_lock():
      pass
    # Enable the internal oscillator
    self.register_set(REG_MODE1, 0b00000001) # Disable response to all call address
    self.register_set(REG_MODE2, 0b00000101) # Outputs are push-pull and high-z when disabled via /OE pin
    self.i2c.unlock()

  # Set the value of a specific register by it's name and mask
  def register_set(self, addr, value, mask=0xFF):
    if (mask != 0xFF):
      _csr = bytearray(1)
      self.i2c.writeto_then_readfrom(self.address, bytes([addr]), _csr)
      value = (int.from_bytes(_csr, "big") & (0xFF - mask)) | value
    self.i2c.writeto(self.address, bytes([addr, value]))

  # set the specificed motor to coast
  def coast(self, motor=0):
    if (motor != 0):
      motor = 2

    while not self.i2c.try_lock():
      pass
    self.register_set(REG_OUTS, OUTPUT_OFF, OUTPUT_MASK[motor]) # Turn output off
    self.register_set(REG_OUTS, OUTPUT_OFF, OUTPUT_MASK[motor + 1]) # Turn output off
    self.i2c.unlock()

  # set the specificed motor to brake
  def brake(self, motor=0):
    if (motor != 0):
      motor = 2

    while not self.i2c.try_lock():
      pass
    self.register_set(REG_OUTS, OUTPUT_ON[motor], OUTPUT_MASK[motor]) # Turn output on
    self.register_set(REG_OUTS, OUTPUT_ON[motor + 1], OUTPUT_MASK[motor + 1]) # Turn output on
    self.i2c.unlock()

  # set a servo to a specific angle
  def servo_angle(self, servo=0, angle=90):
    angle = max(min(int(angle), 180), 0)
    if (servo != 0):
      servo = 1
    while not self.i2c.try_lock():
      pass
    self.register_set(SERVO_ANGLE[servo], angle)
    self.i2c.unlock()

  # detach a servo
  def servo_stop(self, servo=0):
    if (servo != 0):
      servo = 1
    while not self.i2c.try_lock():
      pass
    self.register_set(SERVO_ATTACHED[servo], 0)
    self.i2c.unlock()

  # set the specificed motor to coast
  def set_speed(self, motor=0, speed=0):
    direction = 1
    if (speed < 0):
      direction = 0
      speed = speed * -1
    speed = int(min(speed, 100) * 255 / 100) & 0xFF

    __mp0 = 0 + direction
    __mp1 = 1 - direction
    if (motor != 0):
      __mp0 = 2 + direction
      __mp1 = 3 - direction

    while not self.i2c.try_lock():
      pass
    self.register_set(REG_OUTS, OUTPUT_OFF, OUTPUT_MASK[__mp1]) # Turn output on
    if (speed == 0xFF): 
      self.register_set(REG_OUTS, OUTPUT_ON[__mp0], OUTPUT_MASK[__mp0]) # Turn output to PWM
    else:
      self.register_set(REG_OUTS, OUTPUT_PWM[__mp0], OUTPUT_MASK[__mp0]) # Turn output to PWM
      self.register_set(REG_PWM[__mp0], speed) # PWM output
    self.i2c.unlock()

  # stop and release the motors
  def stop(self):
    while not self.i2c.try_lock():
      pass
    self.register_set(REG_OUTS, 0) # Turn everything off
    self.register_set(SERVO_ATTACHED[0], 0) # Turn everything off
    self.register_set(SERVO_ATTACHED[1], 0) # Turn everything off
    self.i2c.unlock()

  # Allows for use in context managers.
  def __enter__(self):
    return self

  # Automatically de-initialize after a context manager.
  def __exit__(self, exc_type, exc_val, exc_tb):
    self.stop()
    self.deinit(False)

  # De-initialize the i2c.
  def deinit(self, call_stop=True):
    if call_stop:
      self.stop()
    self.i2c.deinit()
