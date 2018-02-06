# ===============================================================================
# Copyright 2015 Jake Ross
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

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.hardware.thermo_spectrometer_controller import HelixController
from pychron.spectrometer.thermo.detector.helix import HelixDetector
from pychron.spectrometer.thermo.magnet.helix import HelixMagnet
from pychron.spectrometer.thermo.source.helix import HelixSource
from pychron.spectrometer.thermo.spectrometer.base import ThermoSpectrometer


class HelixSpectrometer(ThermoSpectrometer):
    magnet_klass = HelixMagnet
    source_klass = HelixSource
    detector_klass = HelixDetector
    microcontroller_klass = HelixController

    def get_command_map(self):
        command_map = dict(ionrepeller='IonRepeller',
                           electronenergy='ElectronEnergy',
                           ysymmetry='YSymmetry',
                           extractionfocus='ExtractionFocus',
                           extractionsymmetry='ExtractionSymmetry',
                           extractionlens='ExtractionLens',
                           ioncountervoltage='IonCounterVoltage',
                           hv='HV')
        return command_map


class HelixPlusSpectrometer(HelixSpectrometer):
    pass
# ============= EOF =============================================



