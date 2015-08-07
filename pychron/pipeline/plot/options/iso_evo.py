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
from traits.api import List, on_trait_change
from traitsui.api import View, VGroup, EnumEditor, Tabbed
# ============= standard library imports ========================
# ============= local library imports  ==========================
# from pychron.processing.fits.iso_evo_fit_selector import IsoFilterFit
from pychron.pipeline.plot.options.figure_plotter_options import object_column, \
    checkbox_column
from pychron.pipeline.plot.options.fit import FitOptions
from pychron.processing.fits.fit import IsoFilterFit
# from pychron.pipeline.plot.options import checkbox_column, \
#     object_column, SaveableFigurePlotterOptions
# from pychron.processing.plot.options import AuxPlotOptions
from pychron.pipeline.plot.options.option import AuxPlotOptions


class IsoFilterFitAuxPlot(AuxPlotOptions, IsoFilterFit):
    names = List
    height = 0
    ofit = None

    # @property
    # def enabled(self):
    # return self.show


class IsotopeEvolutionOptions(FitOptions):
    aux_plot_klass = IsoFilterFitAuxPlot

    # use_plotting = dumpable(Bool)
    # confirm_save = dumpable(Bool)
    # def get_aux_plots(self):
    # return [IsoFilterFit(name='Ar40', fit='linear')]
    # def get_aux_plots(self):
    # for p in self.aux_plots:
    #         print p, p.use, p.enabled

    # def get_saveable_plots(self):
    #     return [p for p in self.aux_plots if p.use]



    @on_trait_change('aux_plots:fit')
    def _handle_fit(self, obj, name, old, new):
        if obj.save_enabled:
            # if new != obj.ofit:
            # self.save_required = True

            obj.ofit = old

    def traits_view(self):
        bg_grp = self._get_bg_group()
        pd_grp = self._get_padding_group()
        a_grp = self._get_axes_group()
        appear_grp = VGroup(bg_grp, pd_grp, a_grp, label='Appearance')

        p_grp = self._get_aux_plots_group()

        v = View(Tabbed(p_grp, appear_grp))
        return v

    # def _get_edit_view(self):
    #     v = View(VGroup(self._get_name_fit_group(),
    #                     Item('marker', editor=EnumEditor(values=marker_names)),
    #                     Item('marker_size'),
    #                     HGroup(Item('ymin', label='Min'),
    #                            Item('ymax', label='Max'),
    #                            show_border=True,
    #                            label='Y Limits'),
    #                     show_border=True))
    #     return v

    def _get_columns(self):
        cols = [object_column(name='name', editable=False),
                checkbox_column(name='plot_enabled', label='Plot'),
                checkbox_column(name='save_enabled', label='Save'),
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



# ============= EOF =============================================