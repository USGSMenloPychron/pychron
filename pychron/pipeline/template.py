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

import yaml
from pyface.message_dialog import warning
from traits.api import HasTraits
from traitsui.api import View, UItem

from pychron.core.ui.strings import PascalCase
from pychron.paths import paths
from pychron.pipeline.nodes import PushNode
from pychron.pipeline.nodes.data import DataNode, UnknownNode, DVCNode, InterpretedAgeNode, ListenUnknownNode
from pychron.pipeline.nodes.diff import DiffNode
from pychron.pipeline.nodes.email import EmailNode
from pychron.pipeline.nodes.find import FindNode
from pychron.pipeline.nodes.gain import GainCalibrationNode
from pychron.pipeline.nodes.geochron import GeochronNode
from pychron.pipeline.nodes.persist import PersistNode, SetInterpretedAgeNode


class PipelineTemplateSaveView(HasTraits):
    name = PascalCase()

    @property
    def path(self):
        if self.name:
            return os.path.join(paths.user_pipeline_template_dir, self.name)

    def traits_view(self):
        v = View(UItem('name'),
                 kind='livemodal', title='New Template Name',
                 resizable=True,
                 buttons=['OK', 'Cancel'])
        return v


class PipelineTemplate(HasTraits):
    def __init__(self, name, path, *args, **kw):
        super(PipelineTemplate, self).__init__(*args, **kw)

        self.name = name
        self.path = path

    def render(self, application, pipeline, bmodel, iabmodel, dvc, clear=True, exclude_klass=None):
        # if first node is an unknowns node
        # render into template
        datanode = None
        try:
            node = pipeline.nodes[0]
            if isinstance(node, DataNode) and not isinstance(node, ListenUnknownNode):
                datanode = node
                datanode.visited = False
        except IndexError:
            pass

        if not datanode:
            datanode = UnknownNode(browser_model=bmodel, dvc=dvc)

        if clear:
            pipeline.nodes = []

        with open(self.path, 'r') as rfile:
            yd = yaml.load(rfile)

        # print self.path, yd
        nodes = yd['nodes']

        if exclude_klass is None:
            exclude_klass = []

        for i, ni in enumerate(nodes):
            # print i, ni
            klass = ni['klass']
            if klass in exclude_klass:
                continue

            if i == 0 and klass == 'UnknownNode':
                pipeline.add_node(datanode)
                continue

            if klass == 'NodeGroup':
                group = pipeline.add_group(ni['name'])
                for nii in ni['nodes']:
                    klass = nii['klass']
                    if klass in exclude_klass:
                        continue

                    node = self._node_factory(klass, nii, application, bmodel, iabmodel, dvc)
                    if node:
                        node.finish_load()
                        group.add_node(node)

            else:
                node = self._node_factory(klass, ni, application, bmodel, iabmodel, dvc)
                if node:
                    node.finish_load()
                    pipeline.add_node(node)

    def _node_factory(self, klass, ni, application, bmodel, iabmodel, dvc):
        mod = __import__('pychron.pipeline.nodes', fromlist=[klass])
        node = getattr(mod, klass)()
        node.pre_load(ni)
        node.load(ni)
        if isinstance(node, InterpretedAgeNode):
            node.trait_set(browser_model=iabmodel, dvc=dvc)
        elif isinstance(node, SetInterpretedAgeNode):
            node.trait_set(dvc=dvc)
        elif isinstance(node, (DVCNode, FindNode)):
            node.trait_set(browser_model=bmodel, dvc=dvc)
        elif isinstance(node, (PersistNode, GainCalibrationNode, PushNode)):
            node.trait_set(dvc=dvc)
        elif isinstance(node, DiffNode):
            recaller = application.get_service('pychron.mass_spec.mass_spec_recaller.MassSpecRecaller')
            node.trait_set(recaller=recaller)
        elif isinstance(node, GeochronNode):
            service = application.get_service('pychron.geochron.geochron_service.GeochronService')
            node.trait_set(service=service)
        elif isinstance(node, EmailNode):
            emailer = application.get_service('pychron.social.email.emailer.Emailer')
            if emailer is None:
                warning(None, 'Cannot load an Email Node, the Email Plugin required.')
                return

            node.trait_set(emailer=emailer)

        return node

# ============= EOF =============================================
