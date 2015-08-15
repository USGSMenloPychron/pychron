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
import os
import pickle

from traits.api import Str, List, Button, Instance, Tuple
from traitsui.api import Controller

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.globals import globalv
from pychron.loggable import Loggable
from pychron.options.ideogram import IdeogramOptions
from pychron.options.options import BaseOptions, SubOptions
from pychron.options.views import IdeogramOptionsView
from pychron.paths import paths


class OptionsManager(Loggable):
    selected = Str
    names = List
    subview_names = Tuple
    subview = Instance(SubOptions)
    selected_subview = Str
    selected_options = Instance(BaseOptions)
    options_klass = None

    id = ''
    _defaults_path = Str

    def __init__(self, *args, **kw):
        super(OptionsManager, self).__init__(*args, **kw)
        self._populate()
        self._initialize()

    def set_selected(self, obj):
        for name in self.names:
            if obj.name == name:
                self.selected_options = obj

    def save(self):
        # dump the default plotter options
        if not os.path.isdir(self.persistence_root):
            try:
                os.mkdir(self.persistence_root)
            except OSError:
                os.mkdir(os.path.dirname(self.persistence_root))
                os.mkdir(self.persistence_root)

        with open(self.selected_options_path, 'w') as wfile:
            pickle.dump(self.selected, wfile)

        with open(os.path.join(self.persistence_root, '{}.p'.format(self.selected)), 'w') as wfile:
            pickle.dump(self.selected_options, wfile)
            #
            # self.plotter_options.dump(self.persistence_root)
            # self._plotter_options_list_dirty = True
            #
            # self.plotter_options = next((pp for pp in self.plotter_options_list if pp.name == name), None)
            # self._dump()

    def factory_default(self):
        if os.path.isfile(self._defaults_path):
            self.selected_options.load_factory_defaults(self._defaults_path)

    def _initialize(self):
        selected = self._load_selected_po()
        self.selected = selected

    def _load_selected_po(self):
        p = self.selected_options_path
        n = 'Default'
        if os.path.isfile(p):
            with open(p, 'r') as rfile:
                try:
                    n = pickle.load(rfile)
                except (pickle.PickleError, EOFError):
                    n = 'Default'
        return n

    def _populate(self):
        self.names = ['Default', 'Foo', 'Bar']

    def _selected_subview_changed(self, new):
        print 'subview changed {}'.format(new)
        self.subview = self.selected_options.get_subview(new)

    def _selected_changed(self, new):
        print 'selected change {}'.format(new)
        if new:
            obj = None
            p = os.path.join(self.persistence_root, '{}.p'.format(new.lower()))
            if os.path.isfile(p):
                try:
                    with open(p, 'r') as rfile:
                        obj = pickle.load(rfile)
                except BaseException:
                    pass

            if obj is None:
                obj = self.options_klass()

            obj.name = new
            self.subview_names = obj.subview_names
            self.selected_options = obj
            self.selected_subview = 'Main'
            # self.selected_options = self.options_klass.open(self.persistence_root, self.id, new)
        else:
            self.selected_options = None

    # def _add_options_fired(self):
    #     info = self.edit_traits(view='new_options_name_view')
    #     if info.result:
    #         self.plotter_options.name = self.new_options_name
    #         self.plotter_options.dump(self.persistence_root)
    #
    #         self._plotter_options_list_dirty = True
    #         self.set_plotter_options(self.new_options_name)

    # def _delete_options_fired(self):
    #     po = self.plotter_options
    #     if self.confirmation_dialog('Are you sure you want to delete {}'.format(po.name)):
    #         p = os.path.join(self.persistence_root, po.name)
    #         os.remove(p)
    #         self._plotter_options_list_dirty = True
    #         self.plotter_options = self.plotter_options_list[0]
    @property
    def selected_options_path(self):
        return os.path.join(self.persistence_root, 'selected.p')

    @property
    def persistence_root(self):
        return os.path.join(paths.plotter_options_dir,
                            globalv.username,
                            self.id)


class FigureOptionsManager(OptionsManager):
    pass


class IdeogramOptionsManager(FigureOptionsManager):
    id = 'ideogram'
    options_klass = IdeogramOptions
    _defaults_path = paths.ideogram_defaults


class OptionsController(Controller):
    delete_options = Button
    add_options = Button
    save_options = Button
    factory_default = Button

    def closed(self, info, is_ok):
        if is_ok:
            self.model.save()

    def controller_delete_options_changed(self, info):
        print 'delete'

    def controller_add_options_changed(self, info):
        print 'add'

    def controller_save_options_changed(self, info):
        print 'save'
        self.model.save()

    def controller_factory_default_changed(self, info):
        print 'factory'
        self.model.factory_default()


if __name__ == '__main__':
    paths.build('_dev')
    # om = IdeogramOptionsManager()
    om = OptionsController(model=IdeogramOptionsManager())
    om.configure_traits(view=IdeogramOptionsView)
# ============= EOF =============================================