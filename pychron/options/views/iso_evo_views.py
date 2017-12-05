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
from traits.api import Bool, Enum, on_trait_change
from traitsui.api import EnumEditor, Item, HGroup, UItem

from pychron.options.options import AppearanceSubOptions, SubOptions, MainOptions, object_column, checkbox_column
from pychron.pychron_constants import FIT_TYPES, FIT_ERROR_TYPES


class IsoEvoSubOptions(SubOptions):
    def traits_view(self):
        return self._make_view(Item('goodness_threshold', label='Intercept Goodness',
                                    tooltip='If % error is greater than "Goodness Threshold" '
                                            'mark regression as "Bad"'),
                               Item('slope_goodness', label='Slope Goodness',
                                    tooltip='If slope of regression is positive and the isotope '
                                            'intensity is greater than "Slope Goodness Intensity" '
                                            'then mark regression as "Bad"'),
                               Item('outlier_goodness', label='Outlier Goodness',
                                    tooltip='If more than "Outlier Goodness" points are identified as outliers'
                                            'then mark regression as "Bad"'),
                               HGroup(Item('curvature_goodness'),
                                      Item('curvature_goodness_at')))


class IsoEvoAppearanceOptions(AppearanceSubOptions):
    pass


class IsoEvoMainOptions(MainOptions):
    plot_enabled = Bool
    save_enabled = Bool
    fit = Enum(FIT_TYPES)
    error_type = Enum(FIT_ERROR_TYPES)
    filter_outliers = Bool

    def _get_global_group(self):
        g = HGroup(
            # Item('controller.plot_enabled', label='Plot'),
            Item('controller.save_enabled', label='Enabled'),
            Item('controller.fit'),
            UItem('controller.error_type', width=-75),
            Item('controller.filter_outliers', label='Filter Outliers'),
            Item('show_sniff'))
        return g

    @on_trait_change('plot_enabled, save_enabled, fit, error_type, filter_outliers')
    def _handle_global(self, name, new):
        self._toggle_attr(name, new)

    def _toggle_attr(self, attr, new):
        items = self.model.selected
        if not items:
            items = self.model.aux_plots

        for a in items:
            setattr(a, attr, new)

    def _get_columns(self):
        cols = [object_column(name='name', editable=False),
                # checkbox_column(name='plot_enabled', label='Plot'),
                checkbox_column(name='save_enabled', label='Enabled'),
                object_column(name='fit',
                              editor=EnumEditor(name='fit_types'),
                              width=75),
                object_column(name='error_type',
                              editor=EnumEditor(name='error_types'),
                              width=75, label='Error'),
                checkbox_column(name='filter_outliers', label='Out.'),
                object_column(name='filter_outlier_iterations', label='Iter.'),
                object_column(name='filter_outlier_std_devs', label='SD'),
                object_column(name='truncate', label='Trunc.'),
                checkbox_column(name='include_baseline_error', label='Inc. BsErr')]
        return cols


VIEWS = {'main': IsoEvoMainOptions,
         'isoevo': IsoEvoSubOptions,
         'appearance': IsoEvoAppearanceOptions}
# ============= EOF =============================================
