# ===============================================================================
# Copyright 2013 Jake Ross
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
from envisage.ui.tasks.task_factory import TaskFactory

from pychron.lasers.tasks.plugins.chromium import ChromiumPlugin
from pychron.lasers.tasks.plugins.laser_plugin import BaseLaserPlugin


class ChromiumCO2Plugin(ChromiumPlugin):
    id = 'pychron.chromium.co2'
    name = 'ChromiumCO2'
    klass = ('pychron.lasers.laser_managers.chromium_laser_manager', 'ChromiumCO2Manager')
    task_name = 'Chromium CO2'
    accelerator = 'Ctrl+Shift+]'
    task_klass = ('pychron.lasers.tasks.laser_task', 'ChromiumCO2Task')


# ============= EOF =============================================
