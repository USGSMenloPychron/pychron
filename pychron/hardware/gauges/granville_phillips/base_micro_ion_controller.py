# ===============================================================================
# Copyright 2017 Jake Ross
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
# =============enthought library imports=======================
from traits.api import List, Str, HasTraits, Float, Int
# =============standard library imports ========================
from numpy import random, char
import time


# =============local library imports  ==========================
class BaseGauge(HasTraits):
    name = Str
    pressure = Float
    display_name = Str
    low = 5e-10
    high = 1e-8
    color_scalar = 1
    width = Int(100)


class BaseMicroIonController(HasTraits):
    address = '01'
    gauges = List
    display_name = Str
    gauge_klass = BaseGauge
    mode = 'rs485'

    def load_additional_args(self, config, *args, **kw):
        self.address = self.config_get(config, 'General', 'address', optional=False)
        self.display_name = self.config_get(config, 'General', 'display_name', default=self.name)
        self.mode = self.config_get(config, 'Communications', 'mode', default='rs485')

        ns = self.config_get(config, 'Gauges', 'names')
        if ns:
            ans = self.config_get(config, 'Gauges', 'display_names', optional=True)
            if not ans:
                ans = ns

            lows = self.config_get(config, 'Gauges', 'lows', optional=True, default='1e-10, 1e-3, 1e-3')
            highs = self.config_get(config, 'Gauges', 'highs', optional=True, default='1e-6, 1, 1')
            cs = self.config_get(config, 'Gauges', 'color_scalars', optional=True, default='1, 1, 1')

            for gi in zip(*map(lambda x: x.split(','), (ns, ans, lows, highs, cs))):
                ni, ai, li, hi, ci = map(str.strip, gi)

                g = self.gauge_klass(name=ni, display_name=ai)
                try:
                    g.low = float(li)
                except ValueError, e:
                    self.warning_dialog('Invalid lows string. {}'.format(e), title=self.config_path)
                    continue

                try:
                    g.high = float(hi)
                except ValueError, e:
                    self.warning_dialog('Invalid highs string. {}'.format(e), title=self.config_path)
                    continue
                try:
                    g.color_scalar = int(ci)
                except ValueError, e:
                    self.warning_dialog('Invalid color_scalar string. {}'.format(e), title=self.config_path)
                    continue

                p = '{}_pressure'.format(ni)
                self.add_trait(p, Float)
                g.on_trait_change(self._pressure_change, 'pressure')

                self.gauges.append(g)

        return True

    def _pressure_change(self, obj, name, old, new):
        self.trait_set(**{'{}_pressure'.format(obj.name): new})

    def get_gauge(self, name):
        return next((gi for gi in self.gauges
                     if gi.name == name or gi.display_name == name), None)

    def _set_gauge_pressure(self, name, v):
        g = self.get_gauge(name)
        if g is not None:
            try:
                g.pressure = float(v)
            except (TypeError, ValueError):
                pass

    def get_pressure(self, name, force=False, verbose=False):
        gauge = self.get_gauge(name)
        if gauge is not None:
            if force:
                self._update_pressure(name, verbose)

            return gauge.pressure

    def get_pressures(self, verbose=False):
        kw = {'verbose': verbose, 'force': True}
        b = self.get_convectron_b_pressure(**kw)
        self._set_gauge_pressure('CG2', b)
        time.sleep(0.05)
        a = self.get_convectron_a_pressure(**kw)
        self._set_gauge_pressure('CG1', a)
        time.sleep(0.05)

        ig = self.get_ion_pressure(**kw)
        self._set_gauge_pressure('IG', ig)

        return ig, a, b

    def set_degas(self, state):
        key = 'DG'
        value = 'ON' if state else 'OFF'
        cmd = self._build_command(key, value)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_degas(self):
        key = 'DGS'
        cmd = self._build_command(key)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_ion_pressure(self, **kw):
        name = 'IG'
        return self._get_pressure(name, **kw)

    def get_convectron_a_pressure(self, **kw):
        name = 'CG1'
        return self._get_pressure(name, **kw)

    def get_convectron_b_pressure(self, **kw):
        name = 'CG2'
        return self._get_pressure(name, **kw)

    def set_ion_gauge_state(self, state):
        key = 'IG1'
        value = 'ON' if state else 'OFF'
        cmd = self._build_command(key, value)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_process_control_status(self, channel=None):
        key = 'PCS'

        cmd = self._build_command(key, channel)

        r = self.ask(cmd)
        r = self._parse_response(r)

        if channel is None:
            if r is None:
                # from numpy import random,char
                r = random.randint(0, 2, 6)
                r = ','.join(char.array(r))

            r = r.split(',')
        return r

    def _get_pressure(self, name, verbose=False, force=False):
        if self._scanning and not force:
            attr = '{}_pressure'.format(name)
            if hasattr(self, attr):
                return getattr(self, attr)

        return self._read_pressure(name, verbose)

    def _update_pressure(self, name, verbose):
        gauge = self.get_gauge(name)
        if gauge:
            p = self._read_pressure(name, verbose)
            gauge.pressure = float(p)

    def _read_pressure(self, name, verbose=False):
        key = 'DS'
        cmd = self._build_command(key, name)

        r = self.ask(cmd, verbose=verbose)
        r = self._parse_response(r, name)
        return r

    def _build_command(self, key, value=None):

        # prepend key with our address
        # example of new string formating
        # see http://docs.python.org/library/string.html#formatspec

        if self.mode == 'rs485':
            key = '#{}{}'.format(self.address, key)

        if value is not None:
            args = (key, value)
        else:
            args = (key,)
        c = ' '.join(args)

        return c

    def _parse_response(self, r, name):
        if self.simulation or r is None:
            from numpy.random import normal

            if name == 'IG':
                loc, scale = 1e-9, 5e-9
            else:
                loc, scale = 1e-2, 5e-3
            return abs(normal(loc, scale))

        return r

# ============= EOF ====================================
