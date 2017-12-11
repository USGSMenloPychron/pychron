# ===============================================================================
# Copyright 2016 ross
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
from traits.api import provides

from pychron.data_mapper.sources.idvc_source import IDVCSource
from pychron.experiment.automated_run.persistence_spec import PersistenceSpec
from pychron.experiment.automated_run.spec import AutomatedRunSpec
from pychron.loggable import Loggable


@provides(IDVCSource)
class DVCSource(Loggable):
    def new_persistence_spec(self):
        pspec = PersistenceSpec()
        rspec = AutomatedRunSpec()
        pspec.run_spec = rspec
        return pspec

    def get_irradiation_import_spec(self, name):
        pass

    def connect(self):
        return True

    def get_irradiation_names(self):
        pass

    def url(self):
        pass
# ============= EOF =============================================
