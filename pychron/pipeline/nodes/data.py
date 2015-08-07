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
from pyface.message_dialog import information
from pyface.timer.do_later import do_after
from traits.api import Instance, Bool, Int, Str, List, Enum
from traitsui.api import View, Item, EnumEditor
# ============= standard library imports ========================
import weakref
from datetime import datetime
# ============= local library imports  ==========================
from pychron.envisage.browser.view import BrowserView
from pychron.pipeline.nodes.base import BaseNode


class DataNode(BaseNode):
    name = 'Data'

    analysis_kind = None
    dvc = Instance('pychron.dvc.dvc.DVC')
    browser_model = Instance('pychron.envisage.browser.browser_model.BrowserModel')

    check_reviewed = Bool(False)

    def configure(self, pre_run=False, **kw):
        if pre_run and getattr(self, self.analysis_kind):
            return True

        if not pre_run:
            self._manual_configured = True

        browser_view = BrowserView(model=self.browser_model)
        info = browser_view.edit_traits(kind='livemodal')

        if info.result:
            records = self.browser_model.get_analysis_records()
            if records:
                analyses = self.dvc.make_analyses(records)
                if browser_view.is_append:
                    ans = getattr(self, self.analysis_kind)
                    ans.extend(analyses)
                else:
                    self.trait_set(**{self.analysis_kind: analyses})

                return True


class UnknownNode(DataNode):
    name = 'Unknowns'
    analysis_kind = 'unknowns'

    def run(self, state):
        if not self.unknowns:
            if not self.configure():
                state.canceled = True
                return

        review_req = []
        unks = self.unknowns
        for ai in unks:
            ai.group_id = 0
            if self.check_reviewed:
                for attr in ('blanks', 'iso_evo'):
                    # check analyses to see if they have been reviewed
                    if attr not in review_req:
                        if not self.dvc.analysis_has_review(ai, attr):
                            review_req.append(attr)

        if review_req:
            information(None, 'The current data set has been '
                              'analyzed and requires {}'.format(','.join(review_req)))

        # add our analyses to the state
        items = getattr(state, self.analysis_kind)
        items.extend(self.unknowns)

        state.projects = {ai.project for ai in state.unknowns}


class ReferenceNode(DataNode):
    name = 'References'
    analysis_kind = 'references'

    def pre_run(self, state):
        self.unknowns = state.unknowns
        refs = state.references
        if refs:
            self.references.extend(refs)

        if not self.references:
            self.configure(pre_run=True)

        return self.references
        # items = getattr(state, self.analysis_kind)
        # if state.has_references:
        #     for ai in self.references:
        #         ai.group_id = 0

        # items.extend(self.references)
        # self.references = items

    def run(self, state):
        pass


class FluxMonitorsNode(DataNode):
    name = 'Flux Monitors'
    analysis_kind = 'flux_monitors'
    auto_configure = False

    def run(self, state):
        items = getattr(state, self.analysis_kind)
        self.unknowns = items

        # if not self.unknowns or state.has_flux_monitors:
        #     self.unknowns = items
        # else:
        #     items.extend(self.unknowns)


class ListenUnknownNode(UnknownNode):
    hours = Int(10)
    mass_spectrometer = Str()
    available_spectrometers = List
    exclude_uuids = List
    period = 60
    mode = Enum('normal')

    def finish_load(self):
        self.available_spectrometers = self.dvc.get_mass_spectrometer_names()

    def configure(self, pre_run=False, *args, **kw):
        if pre_run:
            return True

        return BaseNode.configure(self, pre_run=pre_run, *args, **kw)

    def traits_view(self):
        v = View(Item('hours'),
                 Item('mass_spectrometer', editor=EnumEditor(name='available_spectrometers')),
                 buttons=['OK', 'Cancel'])
        return v

    def post_run(self, engine, state):
        self.engine = weakref.ref(engine)()
        self._start_listening()

    def _start_listening(self):
        self._low = datetime.now()
        self._alive = True
        self._iter()

    def _stop_listening(self):
        pass

    def _iter(self):
        if self._alive:

            unks = self._load_unknowns()
            if unks:
                self.unknowns = unks
                self.exclude_uuids = [u.uuid for u in unks]
                self.engine.refresh_unknowns(unks)

            do_after(self.period * 1000, self._iter)

    def _load_unknowns(self):
        if self.mode == 'normal':
            high = datetime.now()
            low = self._low

        with self.dvc.session_ctx():
            unks = self.dvc.get_analyses_by_date_range(low, high,
                                                       exclude_uuids=self.exclude_uuids,
                                                       analysis_type='unknown',
                                                       mass_spectrometers=self.mass_spectrometer, verbose=True)
            return self.dvc.make_analyses(unks)

# ============= EOF =============================================