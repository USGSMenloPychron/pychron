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
from traits.api import Event, Str, List, Instance, String
# ============= standard library imports ========================
import os
import pickle
# ============= local library imports  ==========================
from pychron.canvas.canvas2D.map_canvas import MapCanvas
from pychron.core.helpers.filetools import list_directory2, add_extension
from pychron.core.ui.stage_component_editor import LaserComponentEditor
from pychron.core.ui.thread import Thread
from pychron.managers.manager import Manager
from pychron.paths import paths
from pychron.stage.maps.base_stage_map import BaseStageMap
from pychron.stage.maps.laser_stage_map import LaserStageMap
from pychron.stage.calibration.tray_calibration_manager import TrayCalibrationManager, get_hole_calibration


def get_stage_map_names(root=None):
    if root is None:
        root = paths.map_dir

    sms = list_directory2(root, '.txt', remove_extension=True)
    print root, sms
    sms = [si for si in sms if not si.endswith('.center')]
    us = list_directory2(paths.user_points_dir, '.yaml', remove_extension=True)
    if us:
        sms.extend(us)
    return sms


class BaseStageManager(Manager):
    keyboard_focus = Event
    canvas_editor_klass = LaserComponentEditor
    tray_calibration_manager = Instance(TrayCalibrationManager)
    stage_map_klass = LaserStageMap
    stage_map_name = Str
    stage_map_names = List
    stage_map = Instance(BaseStageMap)
    canvas = Instance(MapCanvas)

    # root = Str(paths.map_dir)
    calibrated_position_entry = String(enter_set=True, auto_set=False)

    move_thread = None
    temp_position = None
    temp_hole = None
    root = Str
    # use_modified = Bool(True)  # set true to use modified affine calculation
    def motor_event_hook(self, name, value, *args, **kw):
        pass

    def goto_position(self, pos):
        raise NotImplementedError

    def refresh_stage_map_names(self):
        sms = get_stage_map_names(root=self.root)
        self.stage_map_names = sms

    def load(self):
        self.refresh_stage_map_names()

        psm = self._load_previous_stage_map()
        sms = self.stage_map_names
        sm = None
        if psm in sms:
            sm = psm
        elif sms:
            sm = sms[0]

        if sm:
            self.stage_map_name = ''
            self.stage_map_name = sm

    def kill(self):
        r = super(BaseStageManager, self).kill()
        self._save_stage_map()
        return r

    @property
    def stage_map_path(self):
        return os.path.join(paths.hidden_dir, '{}.stage_map'.format(self.id))

    def canvas_editor_factory(self):
        return self.canvas_editor_klass(keyboard_focus='keyboard_focus')

    def move_to_hole(self, hole, **kw):
        self._move(self._move_to_hole, hole, name='move_to_hole', **kw)

    def get_calibrated_position(self, pos, key=None):
        smap = self.stage_map

        # use a affine transform object to map
        canvas = self.canvas
        ca = canvas.calibration_item

        # check if a calibration applies to this hole
        hole_calibration = get_hole_calibration(smap.name, key)
        if hole_calibration:
            self.debug('Using hole calibration')
            ca = hole_calibration

        if ca:
            rot = ca.rotation
            cpos = ca.center
            scale = ca.scale

            self.debug('Calibration parameters: '
                       'rot={:0.3f}, cpos={} scale={:0.3f}'.format(rot, cpos,
                                                                   scale))
            pos = smap.map_to_calibration(pos, cpos, rot,
                                          scale=scale)

        return pos

    def update_axes(self):
        """
        """
        self.info('querying axis positions')
        self._update_axes()

    # private
    def _update_axes(self):
        pass

    def _move_to_hole(self, key, correct_position=True, **kw):
        pass

    def _stop(self):
        pass

    def _move(self, func, pos, name=None, *args, **kw):
        if pos is None:
            return

        if self.move_thread and self.move_thread.isRunning():
            self._stop()

        if name is None:
            name = func.func_name

        self.move_thread = Thread(name='stage.{}'.format(name),
                                  target=func, args=(pos,) + args, kwargs=kw)
        self.move_thread.start()

    def _canvas_factory(self):
        raise NotImplementedError

    def _stage_map_changed_hook(self):
        pass

    # handlers
    def _calibrated_position_entry_changed(self, new):
        self.debug('User entered calibrated position {}'.format(new))
        self.goto_position(new)

    def _stage_map_name_changed(self, new):
        if new:
            self.debug('setting stage map to {}'.format(new))
            root = self.root
            path = os.path.join(root, add_extension(new, '.txt'))
            sm = self.stage_map_klass(file_path=path)

            self.tray_calibration_manager.load_calibration(stage_map=new)

            self.canvas.set_map(sm)
            self.canvas.request_redraw()

            self.stage_map = sm

            self._stage_map_changed_hook()

    # defaults
    def _root_default(self):
        return paths.map_dir

    def _tray_calibration_manager_default(self):
        t = TrayCalibrationManager(parent=self,
                                   canvas=self.canvas)
        return t

    def _canvas_default(self):
        return self._canvas_factory()

    def _save_stage_map(self):
        p = self.stage_map_path
        self.info('saving stage_map {} to {}'.format(self.stage_map_name, p))
        with open(p, 'wb') as f:
            pickle.dump(self.stage_map_name, f)

    def _load_previous_stage_map(self):
        p = self.stage_map_path
        if os.path.isfile(p):
            self.info('loading previous stage map from {}'.format(p))
            with open(p, 'rb') as f:
                try:
                    sm = pickle.load(f)
                    if not sm.endswith('.center'):
                        return sm
                except pickle.PickleError:
                    pass
                    # def traits_view(self):
                    # self.initialize_stage()

# ============= EOF =============================================

# self.stage_maps = []
# config = self.get_configuration()
# if config:
# load the stage maps

# mapfiles = self.config_get(config, 'General', 'mapfiles')
# self.stage_map_names = mapfiles.split(',')
# for mapfile in mapfiles.split(','):
#     path = os.path.join(paths.map_dir, mapfile.strip())
#     sm = StageMap(file_path=path)
#     sm.load_correction_file()
#     self.stage_maps.append(sm)

# load user points as stage map
# for di in os.listdir(paths.user_points_dir):
#     if di.endswith('.yaml'):
#         path = os.path.join(paths.user_points_dir, di)
# sm = self.stage_map_klass(file_path=path)
# self.stage_maps.append(sm)

# load the saved stage map
# sp = self._get_stage_map_by_name(self._load_previous_stage_map())
# if sp is not None:
#     sm = sp

# self.stage_map_name = sm

# load the points file
# self.canvas.load_points_file(self.points_file)

# load defaults
# self._default_z = self.config_get(config, 'Defaults', 'z', default=13, cast='float')

# self.canvas.set_map(sm)
# self.canvas.request_redraw()
