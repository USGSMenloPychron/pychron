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
from pyface.tasks.action.task_action import TaskAction
from traitsui.menu import Action

from pychron.envisage.resources import icon
from pychron.pychron_constants import DVC_PROTOCOL


class SampleEditAction(Action):
    name = 'Sample Edit'
    dname = 'Sample Edit'
    id = 'pychron.sample_entry'

    def perform(self, event):
        from pychron.entry.tasks.sample.sample_edit_view import SampleEditView, SampleEditModel

        app = event.task.window.application
        dvc = app.get_service(DVC_PROTOCOL)
        sem = SampleEditModel(dvc=dvc)
        sem.init()
        sev = SampleEditView(model=sem)
        sev.edit_traits()


class SampleEntryAction(Action):
    name = 'Sample'
    dname = 'Sample'
    id = 'pychron.sample_entry'

    def perform(self, event):
        pid = 'pychron.entry.sample.task'
        app = event.task.window.application
        app.get_task(pid)


class SaveAction(TaskAction):
    name = 'Save'
    image = icon('database-save')
    method = 'save'


class LoadAction(TaskAction):
    name = 'Load'
    image = icon('arrow_up')
    method = 'load'


class DumpAction(TaskAction):
    name = 'Dump'
    image = icon('arrow_down')
    method = 'dump'


class RecoverAction(TaskAction):
    name = 'Recover'
    method = 'recover'


class ClearAction(TaskAction):
    name = 'Clear'
    image = icon('clear')
    method = 'clear'
# ============= EOF =============================================
