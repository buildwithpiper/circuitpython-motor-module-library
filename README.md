# Piper Motor Module
CircuitPython library for the Piper Motor module

The Piper Motor Module is based on the NXP PCA9635 i2c GPIO Expander/LED PWM Driver and two TI DRV8837 Brushed DC Motor Drivers.  It is designed to drive two small geared brished DC motors in a small robotics application.

## Requirements
This library depends on the CircuitPython `busio` (i2c) library, and is connected via i2c.  It should be powered at 5v and use 3.3v logic levels on SDA and SCL.
