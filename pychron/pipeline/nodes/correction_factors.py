# ===============================================================================
# Copyright 2018 ross
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
from pychron.pipeline.editors.correction_factors_editor import CorrectionFactorsEditor
from pychron.pipeline.nodes.base import BaseNode


class CorrectionFactorsNode(BaseNode):
    name = 'Correction Factors'
    auto_configure = False

    def run(self, state):
        editor = CorrectionFactorsEditor()
        self.unknowns = state.unknowns
        editor.analyses = state.unknowns
        editor.initialize()
        state.editors.append(editor)
# ============= EOF =============================================
