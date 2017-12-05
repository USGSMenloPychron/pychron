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
from envisage.ui.tasks.preferences_pane import PreferencesPane
from traits.api import Bool, Str, Enum, File, Directory, \
    Color, Range, Float
from traitsui.api import View, Item, VGroup, HGroup, Group, UItem

from pychron.envisage.tasks.base_preferences_helper import BasePreferencesHelper


class LaserPreferences(BasePreferencesHelper):
    pass


class FusionsLaserPreferences(LaserPreferences):
    use_video = Bool(False)
    video_output_mode = Enum('MPEG', 'Raw')
    ffmpeg_path = File

    video_identifier = Str

    use_media_storage = Bool
    keep_local_copy = Bool
    auto_upload = Bool
    # use_video_server = Bool(False)
    # video_server_port = Int(1084)
    # video_server_quality = Range(1, 75, 75)

    show_grids = Bool(True)
    show_laser_position = Bool(True)
    show_desired_position = Bool(True)
    show_map = Bool(False)

    crosshairs_kind = Enum('BeamRadius', 'UserRadius', 'MaskRadius')
    crosshairs_color = Color('maroon')
    crosshairs_radius = Range(0.0, 10.0, 1.0)

    desired_position_color = Color('green')
    calibration_style = Enum('Tray', 'Free')
    scaling = Range(1.0, 2.0, 1)

    use_autocenter = Bool(False)
    render_with_markup = Bool(False)
    crosshairs_offsetx = Float(0)
    crosshairs_offsety = Float(0)
    crosshairs_offset_color = Color('blue')
    crosshairs_line_width = Float(1.0)
    show_hole = Bool

    show_patterning = Bool(True)
    video_directory = Directory
    use_video_archiver = Bool(True)
    video_archive_months = Range(0, 12, 1)
    video_archive_hours = Range(0, 23, 0)
    video_archive_days = Range(0, 31, 7)

    record_patterning = Bool(False)
    record_brightness = Bool(True)

    use_calibrated_power = Bool(True)
    show_bounds_rect = Bool(True)

    # def _get_value(self, name, value):
    #     if 'color' in name:
    #         value = value.split('(')[1]
    #         value = value[:-1]
    #         value = map(float, value.split(','))
    #         value = ','.join(map(lambda x: str(int(x * 255)), value))
    #     else:
    #         value = super(LaserPreferences, self)._get_value(name, value)
    #     return value


class FusionsDiodePreferences(FusionsLaserPreferences):
    name = 'Fusions Diode'
    preferences_path = 'pychron.fusions.diode'


class FusionsCO2Preferences(FusionsLaserPreferences):
    name = 'Fusions CO2'
    preferences_path = 'pychron.fusions.co2'


class FusionsUVPreferences(FusionsLaserPreferences):
    name = 'Fusions UV'
    preferences_path = 'pychron.fusions.uv'


# ===============================================================================
# Panes
# ===============================================================================
class FusionsLaserPreferencesPane(PreferencesPane):
    def traits_view(self):
        grps = self.get_additional_groups()
        v = View(Group(*grps, layout='tabbed'))
        return v

    def get_additional_groups(self):
        archivergrp = Group(Item('use_video_archiver'),
                            Item('video_archive_days',
                                 label='Archive after N. days',
                                 enabled_when='use_video_archiver'),
                            Item('video_archive_hours',
                                 label='Archive after N. hours',
                                 enabled_when='use_video_archiver'),
                            Item('video_archive_months',
                                 label='Delete after N. months',
                                 enabled_when='use_video_archiver'),
                            show_border=True,
                            label='Archiver')

        recgrp = Group(Item('video_directory', label='Save to',
                            enabled_when='record_lasing_video_video'),
                       show_border=True,
                       label='Record')

        media_storage_grp = VGroup(Item('use_media_storage'),
                                   Item('keep_local_copy'),
                                   Item('auto_upload'))

        videogrp = VGroup(Item('use_video'),
                          VGroup(Item('video_identifier', label='ID',
                                      enabled_when='use_video'),
                                 Item('video_output_mode', label='Output Mode'),
                                 Item('ffmpeg_path', label='FFmpeg Location'),
                                 Item('use_autocenter', label='Auto Center'),
                                 Item('render_with_markup', label='Render Snapshot with markup'),
                                 recgrp,
                                 archivergrp,
                                 media_storage_grp,
                                 enabled_when='use_video'),
                          label='Video')

        canvasgrp = VGroup(Item('show_bounds_rect', label='Display Bounds Rectangle'),
                           Item('show_map', label='Display Map'),
                           Item('show_grids', label='Display Grids'),
                           Item('show_laser_position', label='Display Current Position'),
                           Item('show_desired_position', label='Display Desired Position'),
                           Item('show_hole', label='Display Hole Label'),
                           UItem('desired_position_color', enabled_when='show_desired_position'),
                           Item('crosshairs_kind', label='Crosshairs',
                                enabled_when='show_laser_position'),
                           Item('crosshairs_radius',
                                visible_when='crosshairs_kind=="UserRadius"'),
                           Item('crosshairs_color', enabled_when='show_laser_position'),
                           Item('crosshairs_line_width', enabled_when='show_laser_position'),
                           HGroup(
                               Item('crosshairs_offsetx', label='Offset'),
                               UItem('crosshairs_offsety')),
                           UItem('crosshairs_offset_color'),
                           Item('scaling'),
                           label='Canvas')

        patgrp = Group(Item('record_patterning'),
                       Item('show_patterning'), label='Pattern')
        powergrp = Group(Item('use_calibrated_power'),
                         label='Power')
        return [canvasgrp, videogrp,
                patgrp, powergrp]


class FusionsDiodePreferencesPane(FusionsLaserPreferencesPane):
    category = 'Fusions Diode'
    model_factory = FusionsDiodePreferences


class FusionsCO2PreferencesPane(FusionsLaserPreferencesPane):
    category = 'Fusions CO2'
    model_factory = FusionsCO2Preferences


class FusionsUVPreferencesPane(FusionsLaserPreferencesPane):
    category = 'Fusions UV'
    model_factory = FusionsUVPreferences

# ============= EOF =============================================
