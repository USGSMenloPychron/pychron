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
from pychron.experiment.utilities.identifier import is_special


def retroactive_experiment_identifiers(spec, cruns, active_experiment_identifier):
    if cruns is None:
        cruns = []

    if is_special(spec.identifier):
        cruns.append(spec)
        if active_experiment_identifier:
            spec.experiment_identifier = active_experiment_identifier
    else:
        exp_id = spec.experiment_identifier
        # if cruns:
        #     for c in self._cached_runs:
        #         self.datahub.maintstore.add_experiment_association(c, exp_id)
        #     self._cached_runs = []
        active_experiment_identifier = exp_id

    return cruns, active_experiment_identifier



# ============= EOF =============================================


