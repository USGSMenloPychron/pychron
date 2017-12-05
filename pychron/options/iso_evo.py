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
from traits.api import List, Float, Bool, Int

from pychron.options.aux_plot import AuxPlot
from pychron.options.fit import FitOptions
from pychron.options.views.iso_evo_views import VIEWS
from pychron.processing.fits.fit import IsoFilterFit


class IsoFilterFitAuxPlot(AuxPlot, IsoFilterFit):
    names = List
    height = 0
    ofit = None


class IsotopeEvolutionOptions(FitOptions):
    aux_plot_klass = IsoFilterFitAuxPlot
    subview_names = List(['Main', 'IsoEvo'])
    goodness_threshold = Float  # in percent
    slope_goodness = Float
    outlier_goodness = Int
    curvature_goodness = Float
    curvature_goodness_at = Float
    # _main_options_klass = IsoEvoMainOptions
    show_sniff = Bool(False)

    def _get_subview(self, name):
        return VIEWS[name]

# ============= EOF =============================================
