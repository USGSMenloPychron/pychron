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
import os
from random import random

from numpy import array
from traits.api import Any, cached_property, List, TraitError, Str, Property, Bool

from pychron.core.helpers.filetools import list_directory2
from pychron.globals import globalv
from pychron.paths import paths
from pychron.pychron_constants import NULL_STR
from pychron.spectrometer import get_spectrometer_config_path, get_spectrometer_config_name, \
    set_spectrometer_config_name
from pychron.spectrometer.base_detector import BaseDetector
from pychron.spectrometer.spectrometer_device import SpectrometerDevice


class NoIntensityChange(BaseException):
    pass


class BaseSpectrometer(SpectrometerDevice):
    integration_time = Any
    default_integration_time = 1
    magnet = Any
    source = Any
    magnet_klass = Any
    source_klass = Any
    detector_klass = Any
    microcontroller_klass = Any
    detectors = List
    molecular_weights = None

    reference_detector = Str('H1')
    molecular_weight = Str('Ar40')
    isotopes = Property

    spectrometer_configuration = Str
    spectrometer_configurations = List

    use_deflection_correction = Bool(True)
    use_hv_correction = Bool(True)
    _connection_status = False
    _saved_integration = None
    _debug_values = None

    _test_connect_command = ''

    _config = None

    _prev_signals = None
    _no_intensity_change_cnt = 0

    def convert_to_axial(self, det, v):
        return v

    def make_deflection_dict(self):
        raise NotImplementedError

    def make_configuration_dict(self):
        raise NotImplementedError

    def make_gains_dict(self):
        raise NotImplementedError

    def start(self):
        pass

    def load_configurations(self):
        pass

    def finish_loading(self):
        """
        finish loading magnet
        send configuration if self.send_config_on_startup set in Preferences
        :return:
        """

        if self.microcontroller:
            self.name = self.microcontroller.name

        self.magnet.finish_loading()

        self.test_connection()
        # if self.send_config_on_startup:
        # write configuration to spectrometer
        # self._send_configuration()

    def test_connection(self, force=True):
        """
            if not in simulation mode send a GetIntegrationTime to the spectrometer
            if in simulation mode and the globalv.communication_simulation is disabled
            then return False

        :return: bool
        """
        self.info('testing connnection')
        ret, err = False, ''
        if not self.simulation:
            if force:
                ret = self.ask(self._test_connect_command, verbose=True) is not None
            else:
                ret = self._connection_status
        elif globalv.communication_simulation:
            ret = True

        self._connection_status = ret
        self.microcontroller.set_simulation(not ret)
        return ret, err

    def get_integration_time(self, current=True):
        """
        return current or cached integration time, i.e time between intensity measurements

        :param current: bool, if True retrieve value from qtegra
        :return: float
        """
        if current:
            resp = self.read_integration_time()
            if resp:
                try:
                    self.integration_time = float(resp)
                    self.info(
                        'Integration Time {}'.format(self.integration_time))

                except (TypeError, ValueError, TraitError):
                    self.warning(
                        'Invalid integration time. resp={}'.format(resp))
                    self.integration_time = self.default_integration_time

        return self.integration_time

    def save_integration(self):
        self._saved_integration = self.integration_time

    def restore_integration(self):
        if self._saved_integration:
            self.set_integration_time(self._saved_integration)
            self._saved_integration = None

    def correct_dac(self, det, dac, current=True):
        """
            correct for deflection
            correct for hv
        """
        # correct for deflection
        if self.use_deflection_correction:
            dev = det.get_deflection_correction(current=current)
            dac += dev

        # correct for hv
        # dac *= self.get_hv_correction(current=current)
        if self.use_hv_correction:
            dac = self.get_hv_correction(dac, current=current)
        return dac

    def uncorrect_dac(self, det, dac, current=True):
        """
                inverse of correct_dac
        """

        if self.use_hv_correction:
            dac = self.get_hv_correction(dac, uncorrect=True, current=current)

        if self.use_deflection_correction:
            dac -= det.get_deflection_correction(current=current)
        return dac

    def get_hv_correction(self, dac, uncorrect=False, current=False):
        """
        ion optics correction::

            r=M*v_o/(q*B_o)
            r=M*v_c/(q*B_c)

            E=m*v^2/2
            v=(2*E/m)^0.5

            v_o/B_o = v_c/B_c
            B_c = B_o*v_c/v_o

            B_c = B_o*(E_c/E_o)^0.5

            B_o = B_c*(E_o/E_c)^0.5

            E_o = nominal hv
            E_c = current hv
            B_o = nominal dac
            B_c = corrected dac

        """
        source = self.source
        cur = source.current_hv
        if current:
            cur = source.read_hv()

        if cur is None:
            cor = 1
        else:
            try:
                # cor = source.nominal_hv / cur
                if uncorrect:
                    cor = source.nominal_hv / cur
                else:
                    cor = cur / source.nominal_hv

                cor **= 0.5

            except ZeroDivisionError:
                cor = 1

        dac *= cor
        return dac

    def get_deflection_word(self, keys):
        if self.simulation:
            x = [random.random() for i in keys]
        else:
            x = self.read_deflection_word(keys)
        return x

    def get_parameter_word(self, keys):
        if self.simulation:
            if self._debug_values:
                x = self._debug_values
            else:
                x = [random() for i in keys]
        else:
            x = self.read_parameter_word(keys)

        return x

    def map_isotope(self, mass):
        """
        map a mass to an isotope
        @param mass:
        @return:
        """
        molweights = self.molecular_weights
        # for k, v in molweights.iteritems():
        #     print '\t',k,v,mass, v-mass
        #     if abs(v-mass) < 0.05:
        #         print 'found'
        #         break
        # print molweights, mass

        found = None
        mi = 1
        for k, v in molweights.iteritems():
            d = abs(v - mass)
            if d < 0.15 and d < mi:
                found = k

        if found is None:
            found = 'Iso{:0.4f}'.format(mass)

        return found
        # return next((k for k, v in molweights.iteritems() if abs(v - mass) < 0.15), 'Iso{:0.4f}'.format(mass))

    def map_mass(self, isotope):
        """
        map an isotope to a mass
        @param isotope:
        @return:
        """
        try:
            return self.molecular_weights[isotope]
        except KeyError:
            self.warning('Invalid isotope. Cannot map to a mass. {} not in molecular_weights'.format(isotope))

    def update_isotopes(self, isotope, detector):
        """
        update the isotope name for each detector

        called by AutomatedRun._define_detectors

        :param isotope: str
        :param detector: str or Detector
        :return:
        """
        if isotope != NULL_STR:
            det = self.get_detector(detector)
            if not det:
                self.debug('cannot update detector "{}"'.format(detector))
            else:
                det.isotope = isotope

                self.debug('molweights={}'.format(self.molecular_weights))
                index = det.index
                try:
                    # nmass = int(isotope[2:])
                    nmass = self.map_mass(isotope)
                    for di in self.detectors:
                        mass = nmass - di.index + index

                        # mass = nmass - (di.index + index)

                        isotope = self.map_isotope(mass)
                        self.debug('setting detector {} to {} ({})'.format(di.name, isotope, mass))
                        di.isotope = isotope

                except BaseException, e:
                    self.warning(
                        'Cannot update isotopes. isotope={}, detector={}. error:{}'.format(isotope, detector, e))

    def send_configuration(self, **kw):
        """
            send the configuration values to the device
        """
        self._send_configuration(**kw)

    def _send_configuration(self, **kw):
        raise NotImplementedError

    def _get_cached_config(self):
        if self._config is None:
            p = get_spectrometer_config_path()
            if not os.path.isfile(p):
                self.warning_dialog('Spectrometer configuration file {} not found'.format(p))
                return

            self.debug('caching configuration from {}'.format(p))
            config = self.get_configuration_writer(p)
            d = {}
            defl = {}
            trap = {}
            for section in config.sections():
                if section in ('Default', 'Protection', 'General', 'Trap', 'Magnet'):
                    continue

                for attr in config.options(section):
                    v = config.getfloat(section, attr)
                    if v is not None:
                        if section == 'Deflections':
                            defl[attr.upper()] = v
                        else:
                            d[attr] = v

            section = 'Trap'
            if config.has_section(section):
                for attr in ('current', 'ramp_step', 'ramp_period', 'ramp_tolerance', 'voltage'):
                    if config.has_option(section, attr):
                        trap[attr] = config.getfloat(section, attr)

            section = 'Magnet'
            magnet = {}
            if config.has_section(section):
                for attr in ('mftable',):
                    if config.has_option(section, attr):
                        magnet[attr] = config.get(section, attr)

            if 'hv' in d:
                self.source.nominal_hv = d['hv']

            self._config = (d, defl, trap, magnet)

        return self._config

    def load(self):
        self.load_molecular_weights()
        self.load_detectors()
        self.magnet.load()
        # load local configurations
        self.spectrometer_configurations = list_directory2(paths.spectrometer_config_dir, remove_extension=True,
                                                           extension='.cfg')

        name = get_spectrometer_config_name()
        sc, _ = os.path.splitext(name)
        self.spectrometer_configuration = sc

        p = get_spectrometer_config_path(name)
        config = self.get_configuration_writer(p)

        return config

    def load_molecular_weights(self):
        import csv, yaml
        # load the molecular weights dictionary

        p = os.path.join(paths.spectrometer_dir, 'molecular_weights.csv')
        yp = os.path.join(paths.spectrometer_dir, 'molecular_weights.yaml')
        if os.path.isfile(p):
            self.info('loading "molecular_weights.csv" file. {}'.format(p))
            with open(p, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                mws = {l[0]: float(l[1]) for l in reader}
        elif os.path.isfille(yp):
            self.info('loading "molecular_weights.yaml" file. {}'.format(yp))
            with open(p, 'r') as f:
                mws = yaml.load(f)
        else:
            self.info('writing a default "molecular_weights.csv" file')
            # make a default molecular_weights.csv file
            from pychron.spectrometer.molecular_weights import MOLECULAR_WEIGHTS as mws

            with open(p, 'U' if os.path.isfile(p) else 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                data = [a for a in mws.itervalues()]
                data = sorted(data, key=lambda x: x[1])
                for row in data:
                    writer.writerow(row)

        self.debug('Mol weights {}'.format(mws))
        self.molecular_weights = mws

    def load_detectors(self):
        """
        load setupfiles/spectrometer/detectors.cfg
        populates self.detectors
        :return:
        """
        config = self.get_configuration(path=os.path.join(paths.spectrometer_dir, 'detectors.cfg'))

        for i, name in enumerate(config.sections()):
            relative_position = self.config_get(config, name, 'relative_position', cast='float')

            color = self.config_get(config, name, 'color', default='black')
            default_state = self.config_get(config, name, 'default_state',
                                            default=True, cast='boolean')
            isotope = self.config_get(config, name, 'isotope')
            kind = self.config_get(config, name, 'kind', default='Faraday',
                                   optional=True)
            pt = self.config_get(config, name, 'protection_threshold',
                                 default=None, optional=True, cast='float')

            index = self.config_get(config, name, 'index', cast='float')
            if index is None:
                index = i

            use_deflection = self.config_get(config, name, 'use_deflection', cast='boolean', optional=True)
            if use_deflection is None:
                use_deflection = True

            deflection_correction_sign = 1
            if use_deflection:
                deflection_correction_sign = self.config_get(config, name, 'deflection_correction_sign', cast='int')

            deflection_name = self.config_get(config, name, 'deflection_name', optional=True, default=name)

            self._add_detector(name=name,
                               index=index,
                               relative_position=relative_position,
                               use_deflection=use_deflection,
                               protection_threshold=pt,
                               deflection_correction_sign=deflection_correction_sign,
                               deflection_name=deflection_name,
                               color=color,
                               active=default_state,
                               isotope=isotope,
                               kind=kind)

    # def set_microcontroller(self):
    #     m = self.microcontroller
    #     self.debug('set microcontroller {}'.format(m))
    #     self.magnet.microcontroller = m
    #     self.source.microcontroller = m
    #     for d in self.detectors:
    #         d.microcontroller = m
    #         d.load()
    def get_intensities(self, tagged=True):
        """
        issue a GetData command to Qtegra.

        keys, list of strings
        signals, list of floats::

            keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
            signals = [10,100,1,0.1,1,0.001]

        :param tagged:
        :return: keys, signals
        """
        keys = []
        signals = []
        if self.microcontroller and not self.microcontroller.simulation:
            keys, signals = self.read_intensities()

        if not keys and globalv.communication_simulation:
            keys, signals = self._get_simulation_data()

        signals = array(signals)

        self._check_intensity_no_change(signals)

        for k, v in zip(keys, signals):
            det = self.get_detector(k)
            det.set_intensity(v)

        return keys, signals

    def _check_intensity_no_change(self, signals):
        if self.simulation:
            return

        if self._no_intensity_change_cnt > 25:
            # self.warning_dialog('Something appears to be wrong.\n\n'
            #                     'The detector intensities have not changed in 5 iterations. '
            #                     'Check Qtegra and RemoteControlServer.\n\n'
            #                     'Scan is stopped! Close and reopen window to restart')
            self._no_intensity_change_cnt = 0
            self._prev_signals = None
            raise NoIntensityChange()

        if signals is None:
            self._no_intensity_change_cnt += 1
        elif self._prev_signals is not None:
            try:
                test = (signals == self._prev_signals).all()
            except (AttributeError, TypeError):
                # print 'signals', signals
                # print 'prev_signals', self._prev_signals
                test = True

            if test:
                self.debug('no intensity change cnt= {}'.format(self._no_intensity_change_cnt))
                self.debug('signals={}'.format(signals))
                self.debug('prev_signals={}'.format(self._prev_signals))

                self._no_intensity_change_cnt += 1
            else:
                if self._no_intensity_change_cnt > 0:
                    self.debug('resetting no_intensity_change_cnt')
                    self.debug('signals={}'.format(signals))
                    self.debug('prev_signals={}'.format(self._prev_signals))

                self._no_intensity_change_cnt = 0
                self._prev_signals = None

        self._prev_signals = signals

    def get_intensity(self, dkeys):
        """
            dkeys: str or tuple of strs

        """
        data = self.get_intensities()
        if data is not None:

            keys, signals = data

            def func(k):
                return signals[keys.index(k)] if k in keys else 0

            if isinstance(dkeys, (tuple, list)):
                return [func(key) for key in dkeys]
            else:
                return func(dkeys)
                # return signals[keys.index(dkeys)] if dkeys in keys else 0

    def get_detector(self, name):
        """
        get Detector object by name

        :param name: str
        :return: Detector
        """

        if isinstance(name, BaseDetector):
            return name
        else:
            if name.endswith('_'):
                name = '{})'.format(name[:-1])
                name = name.replace('_', '(')

            return next((det for det in self.detectors if det.name == name), None)

    def read_intensities(self):
        raise NotImplementedError

    def read_deflection_word(self):
        pass

    def read_parameter_word(self):
        pass

    # private
    def _spectrometer_configuration_changed(self, new):
        if new:
            set_spectrometer_config_name(new)

    def _add_detector(self, **kw):
        d = self.detector_klass(spectrometer=self, microcontroller=self.microcontroller, **kw)
        d.load()
        self.detectors.append(d)

    def _magnet_default(self):
        return self.magnet_klass(spectrometer=self, microcontroller=self.microcontroller)

    def _source_default(self):
        return self.source_klass(spectrometer=self, microcontroller=self.microcontroller)

    def _microcontroller_default(self):
        mc = self.microcontroller_klass(name='spectrometer_microcontroller')
        mc.bootstrap()
        return mc

    @cached_property
    def _get_isotopes(self):
        return sorted(self.molecular_weights.keys())

    @property
    def detector_names(self):
        return [di.name for di in self.detectors]

# ============= EOF =============================================
