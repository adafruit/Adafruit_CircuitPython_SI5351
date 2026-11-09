# SPDX-FileCopyrightText: Copyright (c) 2026 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Simple demo of the SI5351C 8-output clock generator.

import board

import adafruit_si5351

i2c = board.I2C()  # uses board.SCL and board.SDA
si5351 = adafruit_si5351.SI5351(i2c)

# Outputs that share a PLL must divide down from the same VCO frequency, and
# configure_frequency() retunes the PLL it is given.  So give each PLL one
# "lead" frequency, then hang other outputs off that PLL with integer dividers.

# PLL A: 10 MHz on CLK0, then integer divisions of the same 900 MHz VCO.
si5351.clock_0.configure_frequency(si5351.pll_a, 10_000_000)  # VCO = 900 MHz
si5351.clock_1.configure_integer(si5351.pll_a, 36)  # 25 MHz
si5351.clock_2.configure_integer(si5351.pll_a, 90)  # 10 MHz
si5351.clock_6.configure_integer(si5351.pll_a, 6)  # 150 MHz (even, 6-254)

# PLL B: 13.56 MHz on CLK3, then more outputs from the same VCO.
si5351.clock_3.configure_frequency(si5351.pll_b, 13_560_000)
si5351.clock_4.configure_integer(si5351.pll_b, 100)
si5351.clock_5.configure_integer(si5351.pll_b, 200)
si5351.clock_5.r_divider = adafruit_si5351.R_DIV_64  # Low frequency output
si5351.clock_7.configure_integer(si5351.pll_b, 254)
si5351.clock_7.r_divider = adafruit_si5351.R_DIV_8

for n in range(8):
    clock = getattr(si5351, f"clock_{n}")
    print(f"Clock {n}: {clock.frequency / 1e6:.6f} MHz")

# Enable the outputs, then check that both PLLs locked.
si5351.outputs_enabled = True
status = si5351.device_status
print("PLL A locked:", not status & adafruit_si5351.STATUS_LOL_A)
print("PLL B locked:", not status & adafruit_si5351.STATUS_LOL_B)

# To lock PLL B to a 10 MHz reference on the CLKIN pin instead (Si5351C):
#   si5351.clkin_frequency = 10_000_000
#   si5351.clkin_divider = adafruit_si5351.CLKIN_DIV_1  # PLL input 10-40 MHz
#   si5351.pll_b.source = adafruit_si5351.PLL_SOURCE_CLKIN
#   si5351.clock_3.configure_frequency(si5351.pll_b, 13_560_000)

while True:
    pass
