# ===============================================================================
# Copyright 2017 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
from traits.api import Float
from traitsui.api import View, Item, RangeEditor

from pychron.spectrometer.spectrometer_device import SpectrometerDevice


class BaseSource(SpectrometerDevice):
    nominal_hv = Float(4500)
    current_hv = Float(4500)

    def sync_parameters(self):
        pass
        # self.read_y_symmetry()
        # self.read_z_symmetry()
        # self.read_trap_current()
        # self.read_hv()



# ============= EOF =============================================
