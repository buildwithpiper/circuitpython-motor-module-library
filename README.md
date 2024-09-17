# Piper Motor Module
CircuitPython library for the Piper Motor module

The Piper Motor Module is modeled after the NXP PCA9635 i2c GPIO Expander/LED PWM Driver and two TI DRV8837 Brushed DC Motor Drivers.  It uses an attiny416 MCU as an i2c peripheral to act as a module that is designed to drive two small geared brished DC motors and or two servos in a small robotics application.

## Requirements
This library depends on the CircuitPython `busio` (i2c) library and is connected via i2c.  It should be powered at 5v and use 3.3v logic levels on SDA and SCL.
