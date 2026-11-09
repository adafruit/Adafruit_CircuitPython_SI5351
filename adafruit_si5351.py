# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_si5351`
====================================================

CircuitPython module to control the SI5351 clock generator.  See
examples/simpletest.py for a demo of the usage.  This is based on the Arduino
library at: https://github.com/adafruit/Adafruit_Si5351_Library/

* Author(s): Tony DiCola
"""

import math

from adafruit_bus_device import i2c_device
from micropython import const

try:
    from typing import Optional, Tuple

    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SI5351.git"


# Internal constants:
_SI5351_ADDRESS = const(0x60)  # Assumes ADDR pin = low
_SI5351_READBIT = const(0x01)
_SI5351_CRYSTAL_FREQUENCY = 25000000.0  # Fixed 25mhz crystal on board.
_SI5351_REGISTER_0_DEVICE_STATUS = const(0)
_SI5351_REGISTER_1_INTERRUPT_STATUS_STICKY = const(1)
_SI5351_REGISTER_2_INTERRUPT_STATUS_MASK = const(2)
_SI5351_REGISTER_3_OUTPUT_ENABLE_CONTROL = const(3)
_SI5351_REGISTER_9_OEB_PIN_ENABLE_CONTROL = const(9)
_SI5351_REGISTER_15_PLL_INPUT_SOURCE = const(15)
_SI5351_REGISTER_16_CLK0_CONTROL = const(16)
_SI5351_REGISTER_17_CLK1_CONTROL = const(17)
_SI5351_REGISTER_18_CLK2_CONTROL = const(18)
_SI5351_REGISTER_19_CLK3_CONTROL = const(19)
_SI5351_REGISTER_20_CLK4_CONTROL = const(20)
_SI5351_REGISTER_21_CLK5_CONTROL = const(21)
_SI5351_REGISTER_22_CLK6_CONTROL = const(22)
_SI5351_REGISTER_23_CLK7_CONTROL = const(23)
_SI5351_REGISTER_24_CLK3_0_DISABLE_STATE = const(24)
_SI5351_REGISTER_25_CLK7_4_DISABLE_STATE = const(25)
_SI5351_REGISTER_26_MULTISYNTHNA_PARAMETERS_1 = const(26)
_SI5351_REGISTER_34_MULTISYNTHNB_PARAMETERS_1 = const(34)
_SI5351_REGISTER_42_MULTISYNTH0_PARAMETERS_1 = const(42)
_SI5351_REGISTER_43_MULTISYNTH0_PARAMETERS_2 = const(43)
_SI5351_REGISTER_44_MULTISYNTH0_PARAMETERS_3 = const(44)
_SI5351_REGISTER_45_MULTISYNTH0_PARAMETERS_4 = const(45)
_SI5351_REGISTER_46_MULTISYNTH0_PARAMETERS_5 = const(46)
_SI5351_REGISTER_47_MULTISYNTH0_PARAMETERS_6 = const(47)
_SI5351_REGISTER_48_MULTISYNTH0_PARAMETERS_7 = const(48)
_SI5351_REGISTER_49_MULTISYNTH0_PARAMETERS_8 = const(49)
_SI5351_REGISTER_50_MULTISYNTH1_PARAMETERS_1 = const(50)
_SI5351_REGISTER_51_MULTISYNTH1_PARAMETERS_2 = const(51)
_SI5351_REGISTER_52_MULTISYNTH1_PARAMETERS_3 = const(52)
_SI5351_REGISTER_53_MULTISYNTH1_PARAMETERS_4 = const(53)
_SI5351_REGISTER_54_MULTISYNTH1_PARAMETERS_5 = const(54)
_SI5351_REGISTER_55_MULTISYNTH1_PARAMETERS_6 = const(55)
_SI5351_REGISTER_56_MULTISYNTH1_PARAMETERS_7 = const(56)
_SI5351_REGISTER_57_MULTISYNTH1_PARAMETERS_8 = const(57)
_SI5351_REGISTER_58_MULTISYNTH2_PARAMETERS_1 = const(58)
_SI5351_REGISTER_59_MULTISYNTH2_PARAMETERS_2 = const(59)
_SI5351_REGISTER_60_MULTISYNTH2_PARAMETERS_3 = const(60)
_SI5351_REGISTER_61_MULTISYNTH2_PARAMETERS_4 = const(61)
_SI5351_REGISTER_62_MULTISYNTH2_PARAMETERS_5 = const(62)
_SI5351_REGISTER_63_MULTISYNTH2_PARAMETERS_6 = const(63)
_SI5351_REGISTER_64_MULTISYNTH2_PARAMETERS_7 = const(64)
_SI5351_REGISTER_65_MULTISYNTH2_PARAMETERS_8 = const(65)
_SI5351_REGISTER_66_MULTISYNTH3_PARAMETERS_1 = const(66)
_SI5351_REGISTER_67_MULTISYNTH3_PARAMETERS_2 = const(67)
_SI5351_REGISTER_68_MULTISYNTH3_PARAMETERS_3 = const(68)
_SI5351_REGISTER_69_MULTISYNTH3_PARAMETERS_4 = const(69)
_SI5351_REGISTER_70_MULTISYNTH3_PARAMETERS_5 = const(70)
_SI5351_REGISTER_71_MULTISYNTH3_PARAMETERS_6 = const(71)
_SI5351_REGISTER_72_MULTISYNTH3_PARAMETERS_7 = const(72)
_SI5351_REGISTER_73_MULTISYNTH3_PARAMETERS_8 = const(73)
_SI5351_REGISTER_74_MULTISYNTH4_PARAMETERS_1 = const(74)
_SI5351_REGISTER_75_MULTISYNTH4_PARAMETERS_2 = const(75)
_SI5351_REGISTER_76_MULTISYNTH4_PARAMETERS_3 = const(76)
_SI5351_REGISTER_77_MULTISYNTH4_PARAMETERS_4 = const(77)
_SI5351_REGISTER_78_MULTISYNTH4_PARAMETERS_5 = const(78)
_SI5351_REGISTER_79_MULTISYNTH4_PARAMETERS_6 = const(79)
_SI5351_REGISTER_80_MULTISYNTH4_PARAMETERS_7 = const(80)
_SI5351_REGISTER_81_MULTISYNTH4_PARAMETERS_8 = const(81)
_SI5351_REGISTER_82_MULTISYNTH5_PARAMETERS_1 = const(82)
_SI5351_REGISTER_83_MULTISYNTH5_PARAMETERS_2 = const(83)
_SI5351_REGISTER_84_MULTISYNTH5_PARAMETERS_3 = const(84)
_SI5351_REGISTER_85_MULTISYNTH5_PARAMETERS_4 = const(85)
_SI5351_REGISTER_86_MULTISYNTH5_PARAMETERS_5 = const(86)
_SI5351_REGISTER_87_MULTISYNTH5_PARAMETERS_6 = const(87)
_SI5351_REGISTER_88_MULTISYNTH5_PARAMETERS_7 = const(88)
_SI5351_REGISTER_89_MULTISYNTH5_PARAMETERS_8 = const(89)
_SI5351_REGISTER_90_MULTISYNTH6_PARAMETERS = const(90)
_SI5351_REGISTER_91_MULTISYNTH7_PARAMETERS = const(91)
_SI5351_REGISTER_092_CLOCK_6_7_OUTPUT_DIVIDER = const(92)
_SI5351_REGISTER_149_SPREAD_SPECTRUM_PARAMETERS = const(149)
_SI5351_REGISTER_165_CLK0_INITIAL_PHASE_OFFSET = const(165)
_SI5351_REGISTER_166_CLK1_INITIAL_PHASE_OFFSET = const(166)
_SI5351_REGISTER_167_CLK2_INITIAL_PHASE_OFFSET = const(167)
_SI5351_REGISTER_168_CLK3_INITIAL_PHASE_OFFSET = const(168)
_SI5351_REGISTER_169_CLK4_INITIAL_PHASE_OFFSET = const(169)
_SI5351_REGISTER_170_CLK5_INITIAL_PHASE_OFFSET = const(170)
_SI5351_REGISTER_177_PLL_RESET = const(177)
_SI5351_REGISTER_183_CRYSTAL_INTERNAL_LOAD_CAPACITANCE = const(183)

# Frequency planning limits
_SI5351_VCO_MIN = const(600000000)  # PLL VCO lock range, low end
_SI5351_VCO_MAX = const(900000000)  # PLL VCO lock range, high end
_SI5351_OUTPUT_MIN = const(8000)  # Lowest output with R divider = 128
_SI5351_OUTPUT_MAX = const(150000000)  # Highest output without DIVBY4
_SI5351_FRACTION_DENOMINATOR = const(0xFFFFF)  # Max fractional resolution
_SI5351_MS_MIN_FREQUENCY = const(600000)  # MS0-MS5 output before R divider
_SI5351_MS_MAX_DIVIDER = const(1800)  # MS0-MS5 largest integer divider
_SI5351_MS67_MIN_FREQUENCY = const(2362205)  # ceil(600 MHz / 254) for MS6/MS7
_SI5351_MS67_MAX_DIVIDER = const(254)  # MS6/MS7 largest (even) divider
_SI5351_CLKIN_PLL_MIN = const(10000000)  # PLL input range when using CLKIN
_SI5351_CLKIN_PLL_MAX = const(40000000)

# User-facing constants:
R_DIV_1 = 0
R_DIV_2 = 1
R_DIV_4 = 2
R_DIV_8 = 3
R_DIV_16 = 4
R_DIV_32 = 5
R_DIV_64 = 6
R_DIV_128 = 7

# PLL reference source (register 15, PLLx_SRC).
PLL_SOURCE_XTAL = 0
PLL_SOURCE_CLKIN = 1  # Si5351C only

# CLKIN pre-divider (register 15, CLKIN_DIV[1:0]).
CLKIN_DIV_1 = 0
CLKIN_DIV_2 = 1
CLKIN_DIV_4 = 2
CLKIN_DIV_8 = 3

# Crystal internal load capacitance (register 183, XTAL_CL[1:0]).
CRYSTAL_LOAD_6PF = 1 << 6
CRYSTAL_LOAD_8PF = 2 << 6
CRYSTAL_LOAD_10PF = 3 << 6

# Status bits.  These share positions in the device status (register 0),
# sticky status (register 1) and interrupt mask (register 2) registers.
STATUS_SYS_INIT = 1 << 7  # Device initializing
STATUS_LOL_B = 1 << 6  # PLL B loss of lock
STATUS_LOL_A = 1 << 5  # PLL A loss of lock
STATUS_LOS_CLKIN = 1 << 4  # CLKIN loss of signal (Si5351C)
STATUS_LOS_XTAL = 1 << 3  # Crystal loss of signal


def _plan_frequency(
    frequency: int, reference: float, min_ms_frequency: int, max_divider: int
) -> Tuple[int, int, int, int]:
    # Port of the Arduino setFrequency() solver.  The output is generated as
    #   fOUT = fREF * (a + b/c) / (D * R)
    # with the fractional part placed on the PLL and the MultiSynth divider D
    # kept an even integer for the lowest jitter.  Returns the PLL multiplier
    # a, the PLL numerator b (over _SI5351_FRACTION_DENOMINATOR), D, and the
    # R divider setting.
    frequency = int(frequency)
    if frequency < _SI5351_OUTPUT_MIN or frequency > _SI5351_OUTPUT_MAX:
        raise ValueError("Frequency must be in range 8 kHz to 150 MHz.")
    # Step 1: engage the R divider until the MultiSynth output is in range.
    ms_frequency = frequency
    r_divider = R_DIV_1
    while ms_frequency < min_ms_frequency and r_divider < R_DIV_128:
        ms_frequency <<= 1
        r_divider += 1
    # Step 2: largest even MultiSynth divider keeping the VCO in band.
    divider = min(_SI5351_VCO_MAX // ms_frequency, max_divider) & ~1
    divider = max(divider, 6)
    vco = ms_frequency * divider
    if vco < _SI5351_VCO_MIN or vco > _SI5351_VCO_MAX:
        raise ValueError("Frequency cannot be generated on this output.")
    # Step 3: fractional PLL multiplier a + b/c.  Float math is used for b so
    # this works on CircuitPython builds without long integer support.
    reference = int(reference)
    multiplier = vco // reference
    remainder = vco % reference
    numerator = int(remainder * (_SI5351_FRACTION_DENOMINATOR / reference))
    numerator = min(numerator, _SI5351_FRACTION_DENOMINATOR - 1)
    if multiplier < 15 or multiplier > 90:
        raise ValueError("Frequency needs a PLL multiplier outside 15 to 90.")
    return multiplier, numerator, divider, r_divider


# Disable invalid name because p1, p2, p3 variables are false positives.
# These are legitimate register names and adding more characters obfuscates
# the intention of the code.

# Disable protected access warning because inner classes by design need and use
# access to protected members.

# Another silly pylint check to disable, it has no context of the complexity
# of R divider values and explicit unrolling of them into multiple if cases
# and return statements.  Disable.


class SI5351:
    """SI5351 clock generator.  Initialize this class by specifying:
     - i2c: The I2C bus connected to the chip.

    Optionally specify:
     - address: The I2C address of the device if it differs from the default.
     - crystal_load: The crystal internal load capacitance, one of
       CRYSTAL_LOAD_6PF, CRYSTAL_LOAD_8PF or CRYSTAL_LOAD_10PF (default).
     - clkin_frequency: The frequency in hertz of the signal on the CLKIN pin
       (Si5351C only).  Required before configuring a PLL whose source is
       PLL_SOURCE_CLKIN, and can also be set later as an attribute.

    Clock outputs are available as clock_0 through clock_7.  clock_0 to
    clock_5 are fractional MultiSynth outputs.  clock_6 and clock_7 (8-output
    parts only) are integer-only outputs with even dividers from 6 to 254.
    """

    # Internal class to represent a PLL on the SI5351.  There are two instances
    # of this, PLL A and PLL B.  Each can be the source for a clock output
    # (with further division performed per clock output).
    class _PLL:
        def __init__(
            self, si5351: "SI5351", base_address: int, clock_control_enabled: bool
        ) -> None:
            self._si5351 = si5351
            self._base = base_address
            self._frequency = None
            self.clock_control_enabled = clock_control_enabled
            # PLLA_SRC is register 15 bit 2 and PLLA_RST is register 177
            # bit 5; PLLB uses bit 3 and bit 7 respectively.
            is_pll_b = base_address == _SI5351_REGISTER_34_MULTISYNTHNB_PARAMETERS_1
            self._source_bit = 3 if is_pll_b else 2
            self._reset_bit = (1 << 7) if is_pll_b else (1 << 5)

        @property
        def frequency(self) -> int:
            """Get the frequency of the PLL in hertz."""
            return self._frequency

        @property
        def source(self) -> int:
            """Get and set the reference source of this PLL, must be one of:
            - PLL_SOURCE_XTAL: the on-board crystal (default)
            - PLL_SOURCE_CLKIN: the external CLKIN pin (Si5351C only)

            Only this PLL's source bit is changed, so the other PLL keeps its
            own source.  The PLL input must be 10 to 40 MHz, so set
            clkin_divider on the SI5351 class if CLKIN is faster than 40 MHz.
            Set the source before configuring the PLL, and configure the PLL
            again after changing it.
            """
            reg_value = self._si5351._read_u8(_SI5351_REGISTER_15_PLL_INPUT_SOURCE)
            return (reg_value >> self._source_bit) & 0x01

        @source.setter
        def source(self, source: int) -> None:
            if source not in {PLL_SOURCE_XTAL, PLL_SOURCE_CLKIN}:
                raise ValueError("Source must be PLL_SOURCE_XTAL or PLL_SOURCE_CLKIN.")
            self._si5351._update_bits(
                _SI5351_REGISTER_15_PLL_INPUT_SOURCE,
                1 << self._source_bit,
                source << self._source_bit,
            )

        def _reference_frequency(self) -> float:
            # Frequency at the PLL input for the currently selected source.
            if self.source == PLL_SOURCE_XTAL:
                return _SI5351_CRYSTAL_FREQUENCY
            clkin_frequency = self._si5351.clkin_frequency
            if clkin_frequency is None:
                raise RuntimeError("clkin_frequency must be set to use the CLKIN source.")
            reference = clkin_frequency / (1 << self._si5351.clkin_divider)
            if reference < _SI5351_CLKIN_PLL_MIN or reference > _SI5351_CLKIN_PLL_MAX:
                raise ValueError("CLKIN / clkin_divider must be in range 10 to 40 MHz.")
            return reference

        def _configure_registers(self, p1: int, p2: int, p3: int) -> None:
            # Update PLL registers.
            with self._si5351._device as i2c:
                buf = self._si5351._BUFFER
                buf[0] = self._base
                buf[1] = (p3 & 0x0000FF00) >> 8
                buf[2] = p3 & 0x000000FF
                buf[3] = (p1 & 0x00030000) >> 16
                buf[4] = (p1 & 0x0000FF00) >> 8
                buf[5] = p1 & 0x000000FF
                buf[6] = ((p3 & 0x000F0000) >> 12) | ((p2 & 0x000F0000) >> 16)
                buf[7] = (p2 & 0x0000FF00) >> 8
                buf[8] = p2 & 0x000000FF
                i2c.write(buf, end=9)
            # Reset both PLLs.
            self._si5351._write_u8(_SI5351_REGISTER_177_PLL_RESET, (1 << 7) | (1 << 5))

        def configure_integer(self, multiplier: int) -> None:
            """Configure the PLL with a simple integer multiplier for the most
            accurate (but more limited) PLL frequency generation.
            """
            if multiplier >= 91 or multiplier <= 14:
                raise ValueError("Multiplier must be in range 14 to 91.")
            multiplier = int(multiplier)
            # Compute register values and configure them.
            p1 = 128 * multiplier - 512
            p2 = 0
            p3 = 1
            self._configure_registers(p1, p2, p3)
            # Calculate exact frequency and store it for reference.
            fvco = self._reference_frequency() * multiplier
            # This should actually take the floor to get the true value but
            # there's a limit on how big a value the floor can be and it's
            # easy to hit with high megahertz frequencies:
            #   https://github.com/adafruit/circuitpython/issues/572
            self._frequency = fvco

        def configure_fractional(self, multiplier: int, numerator: int, denominator: int) -> None:
            """Configure the PLL with a fractional multiplier specified by
            multiplier and numerator/denominator.  This is less accurate and
            susceptible to jitter but allows a larger range of PLL frequencies.
            """
            if multiplier >= 91 or multiplier <= 14:
                raise ValueError("Multiplier must be in range 14 to 91.")
            if denominator > 0xFFFFF or denominator <= 0:  # Prevent divide by zero.
                raise ValueError("Denominator must be greater than 0 and less than 0xFFFFF.")
            if numerator >= 0xFFFFF or numerator < 0:
                raise ValueError("Numerator must be in range 0 to 0xFFFFF.")
            multiplier = int(multiplier)
            numerator = int(numerator)
            denominator = int(denominator)
            # Compute register values and configure them.
            p1 = int(128 * multiplier + math.floor(128 * (numerator / denominator) - 512))
            p2 = int(128 * numerator - denominator * math.floor(128 * (numerator / denominator)))
            p3 = denominator
            self._configure_registers(p1, p2, p3)
            # Calculate exact frequency and store it for reference.
            fvco = self._reference_frequency() * (multiplier + (numerator / denominator))
            # This should actually take the floor to get the true value but
            # there's a limit on how big a value the floor can be and it's
            # easy to hit with high megahertz frequencies:
            #   https://github.com/adafruit/circuitpython/issues/572
            self._frequency = fvco

        def _configure_multiplier(self, multiplier: int, numerator: int) -> None:
            # Apply a multiplier computed by _plan_frequency().
            if numerator == 0:
                self.configure_integer(multiplier)
            else:
                self.configure_fractional(multiplier, numerator, _SI5351_FRACTION_DENOMINATOR)

        def reset(self) -> None:
            """Reset only this PLL.  All outputs using this PLL are briefly
            interrupted.  Call this once after setting the phase_offset of
            every output in a phase-related group that shares this PLL.  The
            reset bit clears itself; this does not wait for the PLL to lock.
            """
            reg_value = self._si5351._read_u8(_SI5351_REGISTER_177_PLL_RESET)
            # Clear both reset bits (preserving reserved bits) so an in-progress
            # reset of the other PLL is not retriggered.
            reg_value &= ~((1 << 7) | (1 << 5)) & 0xFF
            reg_value |= self._reset_bit
            self._si5351._write_u8(_SI5351_REGISTER_177_PLL_RESET, reg_value)

    # Another internal class to represent each fractional clock output.  There
    # are 6 of these (CLK0-CLK5, only CLK0-CLK2 on 3-output parts) and they can
    # each be independently configured to use a specific PLL source and have
    # their own divider on that PLL.
    class _Clock:
        def __init__(
            self,
            si5351: "SI5351",
            base_address: int,
            control_register: int,
            r_register: int,
        ) -> None:
            self._si5351 = si5351
            self._base = base_address
            self._control = control_register
            self._r = r_register
            # CLKx initial phase offset registers are contiguous (165-170).
            self._phase = _SI5351_REGISTER_165_CLK0_INITIAL_PHASE_OFFSET + (
                control_register - _SI5351_REGISTER_16_CLK0_CONTROL
            )
            self._pll = None
            self._divider = None

        @property
        def frequency(self) -> float:  # noqa: PLR0911
            """Get the frequency of this clock output in hertz.  This is
            computed based on the configured PLL, clock divider, and R divider.
            """
            # Make sure a PLL and divider are present, i.e. this clock has
            # been configured, otherwise return nothing.
            if self._pll is None or self._divider is None:
                return None
            # Now calculate frequency as PLL freuqency divided by clock divider.
            base_frequency = self._pll.frequency / self._divider
            # And add a further division for the R divider if set.
            r_divider = self.r_divider
            # Disable should be removed when refactor can be tested.
            if r_divider == R_DIV_1:
                return base_frequency
            elif r_divider == R_DIV_2:
                return base_frequency / 2
            elif r_divider == R_DIV_4:
                return base_frequency / 4
            elif r_divider == R_DIV_8:
                return base_frequency / 8
            elif r_divider == R_DIV_16:
                return base_frequency / 16
            elif r_divider == R_DIV_32:
                return base_frequency / 32
            elif r_divider == R_DIV_64:
                return base_frequency / 64
            elif r_divider == R_DIV_128:
                return base_frequency / 128
            else:
                raise RuntimeError("Unexpected R divider!")

        @property
        def r_divider(self) -> int:
            """Get and set the R divider value, must be one of:
            - R_DIV_1: divider of 1
            - R_DIV_2: divider of 2
            - R_DIV_4: divider of 4
            - R_DIV_8: divider of 8
            - R_DIV_16: divider of 16
            - R_DIV_32: divider of 32
            - R_DIV_64: divider of 64
            - R_DIV_128: divider of 128
            """
            reg_value = self._si5351._read_u8(self._r)
            return (reg_value >> 4) & 0x07

        @r_divider.setter
        def r_divider(self, divider: int) -> None:
            if divider > 7 or divider < 0:
                raise ValueError("Divider must in range 0 to 7.")
            reg_value = self._si5351._read_u8(self._r)
            reg_value &= 0x0F
            divider &= 0x07
            divider <<= 4
            reg_value |= divider
            self._si5351._write_u8(self._r, reg_value)

        @property
        def phase_offset(self) -> int:
            """Initial phase offset of this output, in steps of
            a quarter of the PLL (VCO) period (0 to 127), not degrees.  One
            step is 1 / (4 * PLL frequency) seconds.

            Setting this switches the MultiSynth to fractional mode, which
            phase offsets require (AN619 section 6), even for an offset of 0.
            Configure the PLL and this output first with a divider greater
            than 8, then set the phase offset of every output in the group
            (including the reference output with an offset of 0), then call
            reset() once on their shared PLL.  configure_integer(),
            configure_fractional() and configure_frequency() can restore
            integer mode, so set phase offsets again after calling them.
            """
            return self._si5351._read_u8(self._phase) & 0x7F

        @phase_offset.setter
        def phase_offset(self, offset: int) -> None:
            if offset > 127 or offset < 0:
                raise ValueError("Phase offset must be in range 0 to 127.")
            # Clear MSx_INT (bit 6): phase offsets need fractional mode.
            self._si5351._update_bits(self._control, 1 << 6, 0)
            # Bit 7 is reserved and must be written as 0.
            self._si5351._write_u8(self._phase, int(offset) & 0x7F)

        def _configure_registers(self, p1: int, p2: int, p3: int, divby4: bool = False) -> None:
            # The R divider shares a register with MSx_P1[17:16], so read it
            # first to keep the R divider across reconfiguration.
            r_bits = self._si5351._read_u8(self._r) & 0x70
            # Update MSx registers.
            with self._si5351._device as i2c:
                buf = self._si5351._BUFFER
                buf[0] = self._base
                buf[1] = (p3 & 0x0000FF00) >> 8
                buf[2] = p3 & 0x000000FF
                buf[3] = ((p1 & 0x00030000) >> 16) | r_bits
                if divby4:
                    buf[3] |= 0x0C  # MSx_DIVBY4[1:0] = 11b (AN619 4.1.3)
                buf[4] = (p1 & 0x0000FF00) >> 8
                buf[5] = p1 & 0x000000FF
                buf[6] = ((p3 & 0x000F0000) >> 12) | ((p2 & 0x000F0000) >> 16)
                buf[7] = (p2 & 0x0000FF00) >> 8
                buf[8] = p2 & 0x000000FF
                i2c.write(buf, end=9)

        def configure_integer(self, pll: "PLL", divider: int, inverted: bool = False) -> None:
            """Configure the clock output with the specified PLL source
            (should be a PLL instance on the SI5351 class) and specific integer
            divider.  This is the most accurate way to set the clock output
            frequency but supports less of a range of values.  A divider of 4
            enables the divide-by-4 mode used for outputs above 150 MHz.
            """
            if divider >= 2049 or divider <= 3:
                raise ValueError("Divider must be in range 3 to 2049.")
            divider = int(divider)
            # Make sure the PLL is configured (has a frequency set).
            if pll.frequency is None:
                raise RuntimeError("PLL must be configured.")
            # Compute MSx register values.  For a divider of 4 these work out
            # to the P1=0, P2=0, P3=1 that divide-by-4 mode requires.
            p1 = 128 * divider - 512
            p2 = 0
            p3 = 1
            self._configure_registers(p1, p2, p3, divby4=divider == 4)
            # Configure the clock control register.
            control = 0x0F  # 8mA drive strength, MS0 as CLK0 source,
            # Clock not inverted, powered up
            control |= pll.clock_control_enabled
            control |= 1 << 6  # Enable integer mode.
            if inverted:
                control |= 0b00010000  # Bit 4 of the control register = CLKx_INV
            else:
                control &= 0b11101111  # Make sure to turn it off if not inverted
            self._si5351._write_u8(self._control, control)
            # Store the PLL and divisor value so frequency can be calculated.
            self._pll = pll
            self._divider = divider

        def configure_fractional(
            self,
            pll: "PLL",
            divider: int,
            numerator: int,
            denominator: int,
            inverted: bool = False,
        ) -> None:
            """Configure the clock output with the specified PLL source
            (should be a PLL instance on the SI5351 class) and specific
            fractional divider with numerator/denominator.  Again this is less
            accurate but has a wider range of output frequencies.
            """
            if divider >= 2049 or divider <= 3:
                raise ValueError("Divider must be in range 3 to 2049.")
            if divider == 4:
                # Divide-by-4 mode is integer only (AN619 4.1.3).
                raise ValueError("A divider of 4 requires configure_integer.")
            if denominator > 0xFFFFF or denominator <= 0:  # Prevent divide by zero.
                raise ValueError("Denominator must be greater than 0 and less than 0xFFFFF.")
            if numerator >= 0xFFFFF or numerator < 0:
                raise ValueError("Numerator must be in range 0 to 0xFFFFF.")
            divider = int(divider)
            numerator = int(numerator)
            denominator = int(denominator)
            # Make sure the PLL is configured (has a frequency set).
            if pll.frequency is None:
                raise RuntimeError("PLL must be configured.")
            # Compute MSx register values.
            p1 = int(128 * divider + math.floor(128 * (numerator / denominator)) - 512)
            p2 = int(128 * numerator - denominator * math.floor(128 * (numerator / denominator)))
            p3 = denominator
            self._configure_registers(p1, p2, p3)
            # Configure the clock control register.
            control = 0x0F  # 8mA drive strength, MS0 as CLK0 source,
            # Clock not inverted, powered up
            control |= pll.clock_control_enabled
            if inverted:
                control |= 0b00010000  # Bit 4 of the control register = CLKx_INV
            else:
                control &= 0b11101111  # Make sure to turn it off if not inverted
            self._si5351._write_u8(self._control, control)
            # Store the PLL and divisor value so frequency can be calculated.
            self._pll = pll
            self._divider = divider + (numerator / denominator)

        def configure_frequency(self, pll: "PLL", frequency: int, inverted: bool = False) -> None:
            """Configure the specified PLL, this clock's divider and its R
            divider to generate the requested frequency in hertz (8 kHz to
            150 MHz).  The fractional part is placed on the PLL and this
            output's divider is kept an even integer for the lowest jitter.

            Note this reconfigures the PLL, so any other output already using
            the same PLL will change frequency too.
            """
            multiplier, numerator, divider, r_divider = _plan_frequency(
                frequency,
                pll._reference_frequency(),
                _SI5351_MS_MIN_FREQUENCY,
                _SI5351_MS_MAX_DIVIDER,
            )
            pll._configure_multiplier(multiplier, numerator)
            self.configure_integer(pll, divider, inverted)
            self.r_divider = r_divider

    # Internal class for the integer-only clock outputs CLK6 and CLK7, found on
    # 8-output parts.  Their MultiSynths take a single even divider (6-254)
    # and their R dividers share register 92.
    class _IntegerClock:
        def __init__(
            self,
            si5351: "SI5351",
            divider_register: int,
            control_register: int,
            r_shift: int,
        ) -> None:
            self._si5351 = si5351
            self._base = divider_register
            self._control = control_register
            self._r_shift = r_shift
            self._pll = None
            self._divider = None

        @property
        def frequency(self) -> float:
            """Get the frequency of this clock output in hertz.  This is
            computed based on the configured PLL, clock divider, and R divider.
            """
            # Make sure a PLL and divider are present, i.e. this clock has
            # been configured, otherwise return nothing.
            if self._pll is None or self._divider is None:
                return None
            return self._pll.frequency / self._divider / (1 << self.r_divider)

        @property
        def r_divider(self) -> int:
            """Get and set the R divider value, must be one of:
            - R_DIV_1: divider of 1
            - R_DIV_2: divider of 2
            - R_DIV_4: divider of 4
            - R_DIV_8: divider of 8
            - R_DIV_16: divider of 16
            - R_DIV_32: divider of 32
            - R_DIV_64: divider of 64
            - R_DIV_128: divider of 128
            """
            reg_value = self._si5351._read_u8(_SI5351_REGISTER_092_CLOCK_6_7_OUTPUT_DIVIDER)
            return (reg_value >> self._r_shift) & 0x07

        @r_divider.setter
        def r_divider(self, divider: int) -> None:
            if divider > 7 or divider < 0:
                raise ValueError("Divider must in range 0 to 7.")
            self._si5351._update_bits(
                _SI5351_REGISTER_092_CLOCK_6_7_OUTPUT_DIVIDER,
                0x07 << self._r_shift,
                (divider & 0x07) << self._r_shift,
            )

        def configure_integer(self, pll: "PLL", divider: int, inverted: bool = False) -> None:
            """Configure the clock output with the specified PLL source
            (should be a PLL instance on the SI5351 class) and an even integer
            divider in the range 6 to 254.  CLK6 and CLK7 only support integer
            division, so there is no configure_fractional or phase_offset.
            """
            if divider > 254 or divider < 6 or divider % 2:
                raise ValueError("Divider must be an even number in range 6 to 254.")
            divider = int(divider)
            # Make sure the PLL is configured (has a frequency set).
            if pll.frequency is None:
                raise RuntimeError("PLL must be configured.")
            # MS6/MS7 take the divide ratio directly (AN619 4.1.2).
            self._si5351._write_u8(self._base, divider)
            # Bit 6 of the CLK6/CLK7 control registers is FBA_INT/FBB_INT, the
            # integer mode of the PLL feedback divider rather than of this
            # output, so keep whatever value it already has.
            control = self._si5351._read_u8(self._control) & (1 << 6)
            control |= 0x0F  # 8mA drive strength, MSx as CLKx source, powered up
            control |= pll.clock_control_enabled
            if inverted:
                control |= 0b00010000  # Bit 4 of the control register = CLKx_INV
            self._si5351._write_u8(self._control, control)
            # Store the PLL and divisor value so frequency can be calculated.
            self._pll = pll
            self._divider = divider

        def configure_frequency(self, pll: "PLL", frequency: int, inverted: bool = False) -> None:
            """Configure the specified PLL, this clock's divider and its R
            divider to generate the requested frequency in hertz.  Because the
            divider is limited to 6 to 254, the lowest frequency on CLK6 and
            CLK7 is about 18.5 kHz (the highest is 150 MHz).

            Note this reconfigures the PLL, so any other output already using
            the same PLL will change frequency too.
            """
            multiplier, numerator, divider, r_divider = _plan_frequency(
                frequency,
                pll._reference_frequency(),
                _SI5351_MS67_MIN_FREQUENCY,
                _SI5351_MS67_MAX_DIVIDER,
            )
            pll._configure_multiplier(multiplier, numerator)
            self.configure_integer(pll, divider, inverted)
            self.r_divider = r_divider

    # Class-level buffer to reduce allocations and heap fragmentation.
    # This is not thread-safe or re-entrant by design!
    _BUFFER = bytearray(9)

    def __init__(
        self,
        i2c: I2C,
        *,
        address: int = _SI5351_ADDRESS,
        crystal_load: int = CRYSTAL_LOAD_10PF,
        clkin_frequency: Optional[float] = None,
    ) -> None:
        self._device = i2c_device.I2CDevice(i2c, address)
        self.clkin_frequency = clkin_frequency
        # Setup the SI5351.
        # Disable all outputs setting CLKx_DIS high.
        self._write_u8(_SI5351_REGISTER_3_OUTPUT_ENABLE_CONTROL, 0xFF)
        # Power down all output drivers
        # Class-level buffer to reduce allocations and heap fragmentation.
        # This is not thread-safe or re-entrant by design!
        with self._device as i2c_bus:
            self._BUFFER[0] = _SI5351_REGISTER_16_CLK0_CONTROL
            for i in range(1, 9):
                self._BUFFER[i] = 0x80
            i2c_bus.write(self._BUFFER, end=9)
        # Set the load capacitance for the crystal.
        self.crystal_load = crystal_load
        # Disable spread spectrum output.
        self.spread_spectrum_enabled = False
        # Initialize PLL A and B objects.
        self.pll_a = self._PLL(self, _SI5351_REGISTER_26_MULTISYNTHNA_PARAMETERS_1, 0)
        self.pll_b = self._PLL(self, _SI5351_REGISTER_34_MULTISYNTHNB_PARAMETERS_1, (1 << 5))
        # Initialize the 6 fractional clock outputs.
        self.clock_0 = self._Clock(
            self,
            _SI5351_REGISTER_42_MULTISYNTH0_PARAMETERS_1,
            _SI5351_REGISTER_16_CLK0_CONTROL,
            _SI5351_REGISTER_44_MULTISYNTH0_PARAMETERS_3,
        )
        self.clock_1 = self._Clock(
            self,
            _SI5351_REGISTER_50_MULTISYNTH1_PARAMETERS_1,
            _SI5351_REGISTER_17_CLK1_CONTROL,
            _SI5351_REGISTER_52_MULTISYNTH1_PARAMETERS_3,
        )
        self.clock_2 = self._Clock(
            self,
            _SI5351_REGISTER_58_MULTISYNTH2_PARAMETERS_1,
            _SI5351_REGISTER_18_CLK2_CONTROL,
            _SI5351_REGISTER_60_MULTISYNTH2_PARAMETERS_3,
        )
        self.clock_3 = self._Clock(
            self,
            _SI5351_REGISTER_66_MULTISYNTH3_PARAMETERS_1,
            _SI5351_REGISTER_19_CLK3_CONTROL,
            _SI5351_REGISTER_68_MULTISYNTH3_PARAMETERS_3,
        )
        self.clock_4 = self._Clock(
            self,
            _SI5351_REGISTER_74_MULTISYNTH4_PARAMETERS_1,
            _SI5351_REGISTER_20_CLK4_CONTROL,
            _SI5351_REGISTER_76_MULTISYNTH4_PARAMETERS_3,
        )
        self.clock_5 = self._Clock(
            self,
            _SI5351_REGISTER_82_MULTISYNTH5_PARAMETERS_1,
            _SI5351_REGISTER_21_CLK5_CONTROL,
            _SI5351_REGISTER_84_MULTISYNTH5_PARAMETERS_3,
        )
        # Initialize the 2 integer-only clock outputs.  R6_DIV is register 92
        # bits 2:0 and R7_DIV is bits 6:4.
        self.clock_6 = self._IntegerClock(
            self,
            _SI5351_REGISTER_90_MULTISYNTH6_PARAMETERS,
            _SI5351_REGISTER_22_CLK6_CONTROL,
            0,
        )
        self.clock_7 = self._IntegerClock(
            self,
            _SI5351_REGISTER_91_MULTISYNTH7_PARAMETERS,
            _SI5351_REGISTER_23_CLK7_CONTROL,
            4,
        )

    def _read_u8(self, address: int) -> int:
        # Read an 8-bit unsigned value from the specified 8-bit address.
        with self._device as i2c:
            self._BUFFER[0] = address & 0xFF
            i2c.write(self._BUFFER, end=1)
            i2c.readinto(self._BUFFER, end=1)
        return self._BUFFER[0]

    def _write_u8(self, address: int, val: int) -> None:
        # Write an 8-bit unsigned value to the specified 8-bit address.
        with self._device as i2c:
            self._BUFFER[0] = address & 0xFF
            self._BUFFER[1] = val & 0xFF
            i2c.write(self._BUFFER, end=2)

    def _update_bits(self, address: int, mask: int, val: int) -> None:
        # Read-modify-write only the bits in mask at the specified address.
        reg_value = self._read_u8(address)
        reg_value = (reg_value & ~mask) | (val & mask)
        self._write_u8(address, reg_value)

    @property
    def outputs_enabled(self) -> bool:
        """Get and set the enabled state of all clock outputs as a boolean.
        If true then all clock outputs are enabled, and if false then they are
        all disabled.
        """
        # Register 3 bits are output *disable* bits, so 0x00 = all enabled.
        return self._read_u8(_SI5351_REGISTER_3_OUTPUT_ENABLE_CONTROL) == 0x00

    @outputs_enabled.setter
    def outputs_enabled(self, val: bool) -> None:
        if not val:
            self._write_u8(_SI5351_REGISTER_3_OUTPUT_ENABLE_CONTROL, 0xFF)
        else:
            self._write_u8(_SI5351_REGISTER_3_OUTPUT_ENABLE_CONTROL, 0x00)
        self.reset_plls()

    def reset_plls(self) -> None:
        """Reset both PLLs. This is required when the phase between clocks
        needs to be non-random.

        See e.g.

            https://groups.io/g/BITX20/topic/si5351a_facts_and_myths/5430607
        """
        self._write_u8(_SI5351_REGISTER_177_PLL_RESET, (1 << 7) | (1 << 5))

    @property
    def clkin_divider(self) -> int:
        """Get and set the CLKIN pre-divider (Si5351C only), must be one of:
        - CLKIN_DIV_1: divider of 1
        - CLKIN_DIV_2: divider of 2
        - CLKIN_DIV_4: divider of 4
        - CLKIN_DIV_8: divider of 8

        This is shared by both PLLs.  Pick a divider that brings the CLKIN
        signal into the 10 to 40 MHz PLL input range.
        """
        reg_value = self._read_u8(_SI5351_REGISTER_15_PLL_INPUT_SOURCE)
        return (reg_value >> 6) & 0x03

    @clkin_divider.setter
    def clkin_divider(self, divider: int) -> None:
        if divider > 3 or divider < 0:
            raise ValueError("Divider must be in range 0 to 3.")
        self._update_bits(_SI5351_REGISTER_15_PLL_INPUT_SOURCE, 0xC0, divider << 6)

    @property
    def crystal_load(self) -> int:
        """Get and set the crystal internal load capacitance, must be one of:
        - CRYSTAL_LOAD_6PF: 6 pF
        - CRYSTAL_LOAD_8PF: 8 pF
        - CRYSTAL_LOAD_10PF: 10 pF
        """
        return self._read_u8(_SI5351_REGISTER_183_CRYSTAL_INTERNAL_LOAD_CAPACITANCE) & 0xC0

    @crystal_load.setter
    def crystal_load(self, load: int) -> None:
        if load not in {CRYSTAL_LOAD_6PF, CRYSTAL_LOAD_8PF, CRYSTAL_LOAD_10PF}:
            raise ValueError(
                "Load must be CRYSTAL_LOAD_6PF, CRYSTAL_LOAD_8PF or CRYSTAL_LOAD_10PF."
            )
        # AN619: reserved bits 5:0 should be written as 010010b.
        self._write_u8(_SI5351_REGISTER_183_CRYSTAL_INTERNAL_LOAD_CAPACITANCE, load | 0x12)

    @property
    def spread_spectrum_enabled(self) -> bool:
        """Get and set the spread spectrum enable bit (SSC_EN) as a boolean.
        Spread spectrum only applies to outputs using PLL A, and this does not
        program the spread spectrum parameters (registers 149-161).
        """
        reg_value = self._read_u8(_SI5351_REGISTER_149_SPREAD_SPECTRUM_PARAMETERS)
        return bool(reg_value & 0x80)

    @spread_spectrum_enabled.setter
    def spread_spectrum_enabled(self, val: bool) -> None:
        self._update_bits(
            _SI5351_REGISTER_149_SPREAD_SPECTRUM_PARAMETERS, 0x80, 0x80 if val else 0x00
        )

    @property
    def device_status(self) -> int:
        """Get the device status register as an integer.  Test it against the
        STATUS_SYS_INIT, STATUS_LOL_B, STATUS_LOL_A, STATUS_LOS_CLKIN and
        STATUS_LOS_XTAL bit constants.
        """
        return self._read_u8(_SI5351_REGISTER_0_DEVICE_STATUS)

    @property
    def sticky_status(self) -> int:
        """Get the sticky interrupt status register as an integer.  Each bit
        stays set (see the STATUS_* constants) until clear_sticky_status() is
        called.
        """
        return self._read_u8(_SI5351_REGISTER_1_INTERRUPT_STATUS_STICKY)

    def clear_sticky_status(self) -> None:
        """Clear all sticky interrupt status flags."""
        self._write_u8(_SI5351_REGISTER_1_INTERRUPT_STATUS_STICKY, 0x00)

    @property
    def interrupt_mask(self) -> int:
        """Get and set the interrupt mask register as an integer.  A 1 in a
        STATUS_* bit position stops that condition from pulling the INTR pin
        low (Si5351C only).
        """
        return self._read_u8(_SI5351_REGISTER_2_INTERRUPT_STATUS_MASK)

    @interrupt_mask.setter
    def interrupt_mask(self, mask: int) -> None:
        self._write_u8(_SI5351_REGISTER_2_INTERRUPT_STATUS_MASK, mask)

    @property
    def oeb_pin_mask(self) -> int:
        """Get and set the OEB pin enable mask as an integer.  A 0 in bit N
        means the OEB pin controls CLKN's output enable, and a 1 means CLKN
        ignores the OEB pin.  The power-on default of 0 lets OEB control every
        output.
        """
        return self._read_u8(_SI5351_REGISTER_9_OEB_PIN_ENABLE_CONTROL)

    @oeb_pin_mask.setter
    def oeb_pin_mask(self, mask: int) -> None:
        self._write_u8(_SI5351_REGISTER_9_OEB_PIN_ENABLE_CONTROL, mask)
