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
PCA9635_ADDR = 0x0F

# Register addresses and masks
MASK_MODE = 0xFF
REG_MODE1 = 0x00
REG_MODE2 = 0x01

MASK_PWM = 0xFF
REG_PWM0 = 0x02
REG_PWM1 = 0x03
REG_PWM2 = 0x04
REG_PWM3 = 0x05
REG_OUTS = 0x14

OUTPUT0_ON   = 0b00000001
OUTPUT0_OFF  = 0b00000000
OUTPUT0_PWM  = 0b00000010
OUTPUT0_MASK = 0b00000011

OUTPUT1_ON   = 0b00000100
OUTPUT1_OFF  = 0b00000000
OUTPUT1_PWM  = 0b00001000
OUTPUT1_MASK = 0b00001100

OUTPUT2_ON   = 0b00010000
OUTPUT2_OFF  = 0b00000000
OUTPUT2_PWM  = 0b00100000
OUTPUT2_MASK = 0b00110000

OUTPUT3_ON   = 0b01000000
OUTPUT3_OFF  = 0b00000000
OUTPUT3_PWM  = 0b10000000
OUTPUT3_MASK = 0b11000000



# ----------- Methods -----------
class piper_motor_module:
  # Initialize the sensor
  def __init__(self, i2c, address=PCA9635_ADDR):

    self.i2c = i2c
    self.address = address

    self.i2c.try_lock()

    # Enable the internal oscillator
    self.register_set(REG_MODE1, MASK_MODE, 0b00000001) # Disable response to all call address
    self.register_set(REG_MODE2, MASK_MODE, 0b00000101) # Outputs are push-pull and high-z when disabled via /OE pin

    self.i2c.unlock()


  # Invert the bits in a 8-bit (or otherwise specified) number
  def bit_not(self, n, numbits=8):
    return (1 << numbits) - 1 - n

  # Get the value of a specific register by it's name and mask
  def register_get(self, addr, mask):
    _csr = bytearray(1)
    self.i2c.writeto_then_readfrom(self.address, bytes([addr]), _csr)
    _value = int.from_bytes(_csr, "big") & mask
    return _value

  # Set the value of a specific register by it's name and mask
  def register_set(self, addr, mask, value):
    if (mask != 0xFF):
      _csr = self.register_get(addr, 0xFF)
      _csr = _csr & self.bit_not(mask)
      value = _csr | value
    _csr = ((addr << 8) | value).to_bytes(2, 'big')
    self.i2c.writeto(self.address, _csr)

  # set the specificed motor to coast
  def coast(self, motor=0):
    while not self.i2c.try_lock():
      pass

    if (motor == 0):
      self.register_set(REG_OUTS, OUTPUT0_MASK, OUTPUT0_OFF) # Turn output 0 off
      self.register_set(REG_OUTS, OUTPUT1_MASK, OUTPUT1_OFF) # Turn output 1 off
    else:
      self.register_set(REG_OUTS, OUTPUT2_MASK, OUTPUT2_OFF) # Turn output 2 off
      self.register_set(REG_OUTS, OUTPUT3_MASK, OUTPUT3_OFF) # Turn output 3 off

    self.i2c.unlock()

  # set the specificed motor to brake
  def brake(self, motor=0):
    while not self.i2c.try_lock():
      pass

    if (motor == 0):
      self.register_set(REG_OUTS, OUTPUT0_MASK, OUTPUT0_ON) # Turn output 0 off
      self.register_set(REG_OUTS, OUTPUT1_MASK, OUTPUT1_ON) # Turn output 1 off
    else:
      self.register_set(REG_OUTS, OUTPUT2_MASK, OUTPUT2_ON) # Turn output 2 off
      self.register_set(REG_OUTS, OUTPUT3_MASK, OUTPUT3_ON) # Turn output 3 off

    self.i2c.unlock()

  # stop the motors (coast)
  def stop(self):
    self.register_set(REG_OUTS, 0xFF, 0) # Turn everything off

  # set the specificed motor to coast
  def set_speed(self, motor=0, speed=0):
    direction = 1
    if (speed < 0):
      direction = 0
      speed = speed * -1
    if (speed > 100):
      speed = 100

    speed = int(speed * 255 / 100) & 0xFF
    print("speed =", speed)

    while not self.i2c.try_lock():
      pass

    if (motor == 0):
      if (direction == 0):
        self.register_set(REG_OUTS, OUTPUT1_MASK, OUTPUT1_OFF) # Turn output 1 on
        if (speed == 0xFF): 
          self.register_set(REG_OUTS, OUTPUT0_MASK, OUTPUT0_ON) # Turn output 0 to PWM
        else:
          self.register_set(REG_OUTS, OUTPUT0_MASK, OUTPUT0_PWM) # Turn output 0 to PWM
          self.register_set(REG_PWM0, MASK_PWM, speed) # PWM output 0
      else:
        self.register_set(REG_OUTS, OUTPUT0_MASK, OUTPUT0_OFF) # Turn output 0 on
        if (speed == 0xFF):
          self.register_set(REG_OUTS, OUTPUT1_MASK, OUTPUT1_ON) # Turn output 0 on
        else:
          self.register_set(REG_OUTS, OUTPUT1_MASK, OUTPUT1_PWM) # Turn output 1 to PWM
          self.register_set(REG_PWM1, MASK_PWM, speed) # PWM output 1
    else:
      if (direction == 0):
        self.register_set(REG_OUTS, OUTPUT3_MASK, OUTPUT3_OFF) # Turn output 3 on
        if (speed == 0xFF):
          self.register_set(REG_OUTS, OUTPUT2_MASK, OUTPUT2_ON) # Turn output 2 to PWM
        else:
          self.register_set(REG_OUTS, OUTPUT2_MASK, OUTPUT2_PWM) # Turn output 2 to PWM
          self.register_set(REG_PWM2, MASK_PWM, speed) # PWM output 2
      else:
        self.register_set(REG_OUTS, OUTPUT2_MASK, OUTPUT2_OFF) # Turn output 2 on
        if (speed == 0xFF):
          self.register_set(REG_OUTS, OUTPUT3_MASK, OUTPUT3_ON) # Turn output 3 to PWM
        else:
          self.register_set(REG_OUTS, OUTPUT3_MASK, OUTPUT3_PWM) # Turn output 3 to PWM
          self.register_set(REG_PWM3, MASK_PWM, speed) # PWM output 3

    self.i2c.unlock()

  # Allows for use in context managers.
  def __enter__(self):
    return self

  # Automatically de-initialize after a context manager.
  def __exit__(self, exc_type, exc_val, exc_tb):
    self.stop()
    self.deinit()

  # De-initialize the sig pin.
  def deinit(self):
    self.stop()
    self.i2c.deinit()
