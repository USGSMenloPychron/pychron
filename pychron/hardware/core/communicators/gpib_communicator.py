# ===============================================================================
# Copyright 2011 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
# from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
# from traitsui.api import View, Item, Group, HGroup, VGroup

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.hardware.core.communicators.communicator import Communicator
from pychron.hardware.core.communicators.visa import resource_manager


class GpibCommunicator(Communicator):
    """
        uses PyVisa as main interface to GPIB. currently (8/27/14) need to use a 32bit python version.
        The NI488.2 framework does not work with a 64bit distribution
    """

    primary_address = 0
    secondary_address = 0

    def open(self, *args, **kw):
        self.debug('openning gpib communicator')
        self.handle = resource_manager.get_instrument('GPIB{}::{}::INSTR'.format(self.primary_address,
                                                                                 self.secondary_address))
        if self.handle is not None:
            self.simulation = False
            return True

    def load(self, config, path, **kw):
        self.set_attribute(config, 'primary_address', 'Communications', 'primary_address')
        self.set_attribute(config, 'secondary_address', 'Communications', 'secondary_address', optional=False)
        return True

    def trigger(self):
        self.handle.trigger()

    def ask(self, cmd):
        return self.handle.ask(cmd)

    def tell(self, cmd):
        self.handle.write(cmd)

# address = 16
#
#     def load(self, config, path):
#         return True
#
#     def open(self, *args, **kw):
#         try:
#             self.handle = cdll.LoadLibrary(NI_PATH)
#         except:
#             return False
#
#         self.dev_handle = self.handle.ibdev(0, self.address, 0, 4, 1, 0)
#         return True
# #        print self.dev_handle
# #        if self.dev_handle < 0:
# #            self.simulation = True
# #        else:
# #            self.simulation = False
# #
# #
# #        print self.simulation, 'fff'
# #        return not self.simulation
#
#     def ask(self, cmd, verbose=True, *args, **kw):
# #        self.handle.ibask(self.dev_handle)
#         if self.handle is None:
#             if verbose:
#                 self.info('no handle    {}'.format(cmd.strip()))
#             return
#
#         self._lock.acquire()
#         r = ''
#         retries = 5
#         i = 0
#         while len(r) == 0 and i < retries:
#             self._write(cmd)
#             time.sleep(0.05)
#             r = self._read()
#
#             i += 1
#
#         if verbose:
#             self.log_response(cmd, r)
#
#         self.handle.ibclr(self.dev_handle)
#         self._lock.release()
#
#         return r
#
#     def tell(self, *args, **kw):
#         self.write(*args, **kw)
#
#     def write(self, cmd, verbose=True, *args, **kw):
#
#         self._write(cmd, *args, **kw)
#         if verbose:
#             self.info(cmd)
#
#     def _write(self, cmd, *args, **kw):
#         if self.simulation:
#             pass
#         else:
#             cmd += self._terminator
#             self.handle.ibwrt(self.dev_handle, cmd, len(cmd))
#
#     def _read(self):
#         if self.simulation:
#             pass
#         else:
#             b = create_string_buffer('\0' * 4096)
#             retries = 10
#             i = 0
#             while len(b.value) == 0 and i <= retries:
#                 self.handle.ibrd(self.dev_handle, b, 4096)
#                 i += 1
#             return b.value.strip()
#
# if __name__ == '__main__':
#     g = GPIBCommunicator()
#     g.open()
#
#     print g.tell('1HX')
# #    print g.ask('2TP?')

# ============= EOF ====================================
