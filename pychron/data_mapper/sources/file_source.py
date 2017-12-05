# ===============================================================================
# Copyright 2016 ross
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

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.data_mapper.sources.dvc_source import DVCSource


class FileSource(DVCSource):
    _delimiter = ','

    def file_gen(self, p, delimiter):
        if delimiter is None:
            delim = self._delimiter

        def gen():
            with open(p, 'r') as rfile:
                for line in rfile:
                    yield line.strip().split(delim)

        return gen()

# ============= EOF =============================================
