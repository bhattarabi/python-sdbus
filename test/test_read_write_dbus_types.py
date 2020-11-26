# SPDX-License-Identifier: LGPL-2.1-or-later

# Copyright (C) 2020  igo95862

# This file is part of py_sd_bus

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from unittest import TestCase, main

from py_sd_bus import get_default_bus


class TestDbusTypes(TestCase):
    def setUp(self) -> None:
        self.bus = get_default_bus()
        self.message = self.bus.new_method_call_message(
            'org.freedesktop.systemd1',
            '/org/freedesktop/systemd1',
            'org.freedesktop.systemd1.Manager',
            'GetUnit')

    def test_unsigned(self) -> None:
        int_t_max = 2**64
        unsigned_integers = ((2**8)-1, (2**16)-1, (2**32)-1, int_t_max-1)
        self.message.append_basic("yqut", *unsigned_integers)
        # Test overflows
        self.assertRaises(
            OverflowError, self.message.append_basic, "t", 2**64)

        self.assertRaises(
            OverflowError, self.message.append_basic, "y", -1)
        self.assertRaises(
            OverflowError, self.message.append_basic, "q", -1)
        self.assertRaises(
            OverflowError, self.message.append_basic, "u", -1)
        self.assertRaises(
            OverflowError, self.message.append_basic, "t", -1)

        self.message.seal()
        return_integers = tuple(self.message.iter_contents())
        self.assertEqual(unsigned_integers, return_integers)

    def test_signed(self) -> None:
        int_n_max = (2**(16-1))-1
        int_i_max = (2**(32-1))-1
        int_x_max = (2**(64-1))-1
        signed_integers_positive = (int_n_max, int_i_max, int_x_max)
        self.message.append_basic("nix", *signed_integers_positive)

        self.assertRaises(
            OverflowError, self.message.append_basic, "x", int_x_max + 1)

        int_n_min = -(2**(16-1))
        int_i_min = -(2**(32-1))
        int_x_min = -(2**(64-1))
        signed_integers_negative = (int_n_min, int_i_min, int_x_min)
        self.message.append_basic("n", int_n_min)
        self.message.append_basic("i", int_i_min)
        self.message.append_basic("x", int_x_min)
        self.assertRaises(
            OverflowError, self.message.append_basic, "x", int_x_min - 1)

        self.message.seal()
        return_integers = tuple(self.message.iter_contents())
        self.assertEqual(signed_integers_positive +
                         signed_integers_negative, return_integers)

    def test_strings(self) -> None:
        test_string = "test"
        test_path = "/test/object"
        test_signature = "say(xsai)o"

        self.message.append_basic("s", test_string)
        self.message.append_basic("o", test_path)
        self.message.append_basic("g", test_signature)

        self.message.seal()
        self.assertEqual(tuple(self.message.iter_contents()),
                         (test_string, test_path, test_signature))

    def test_double(self) -> None:
        test_double = 1.0
        self.message.append_basic("d", test_double)

        self.message.seal()
        self.assertEqual(tuple(self.message.iter_contents()), (test_double,))


if __name__ == "__main__":
    main()
