# ===============================================================================
# Copyright 2016 Jake Ross
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
from pyface.message_dialog import warning
from traits.api import HasTraits, Str, Int, Bool, Any, Float, Property, on_trait_change, Button
from traitsui.api import View, UItem, Item, HGroup, VGroup, TextEditor

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.hardware.core.communicators.ethernet_communicator import EthernetCommunicator


class FirmwareClient(HasTraits):
    command = Str(enter_set=True, auto_set=False)
    responses = Str

    send_button = Button('Send')

    host = Str
    port = Int

    def __init__(self, *args, **kw):
        super(FirmwareClient, self).__init__(*args, **kw)

        c = EthernetCommunicator(host=self.host, port=self.port)
        self._comm = c

    def test_connection(self):
        if not self._comm.open():
            warning(None, 'Could not connect to {}:{}'.format(self.host, self.port))
        else:
            return True

    def _send(self):
        cmd = self.command
        resp = self._comm.ask(cmd)
        resp = '{} ==> {}'.format(cmd, resp)
        self.responses = '{}\n{}'.format(self.responses, resp)

    # handlers
    def _send_button_fired(self):
        self._send()

    def _command_changed(self):
        self._send()

    def traits_view(self):
        v = View(VGroup(HGroup(Item('command'), UItem('send_button')),
                        UItem('responses', style='custom',
                              editor=TextEditor(read_only=True))),
                 title='Furnace Firmware Client',
                 resizable=True)
        return v


if __name__ == '__main__':
    c = FirmwareClient(host='192.168.0.141', port=4567)
    if c.test_connection():
        c.configure_traits()
# ============= EOF =============================================