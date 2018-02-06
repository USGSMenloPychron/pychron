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

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
import base64
import struct


def format_blob(blob):
    return base64.b64decode(blob)


def encode_blob(blob):
    # print len(blob), len(base64.b64encode(blob))
    return base64.b64encode(blob)


def pack(fmt, data):
    """
    data should be something like [(x0,y0),(x1,y1), (xN,yN)]
    @param fmt:
    @param data:
    @return:
    """
    # if len(args) > 1:
    #     args = zip(args)
    return ''.join([struct.pack(fmt, *datum) for datum in data])


def unpack(blob, fmt='>ff', step=8, decode=False):
    if decode:
        blob = format_blob(blob)

    if blob:
        try:
            return zip(*[struct.unpack(fmt, blob[i:i + step]) for i in xrange(0, len(blob), step)])
        except struct.error:
            ret = []
            for i in xrange(0, len(blob), step):
                try:
                    args = struct.unpack(fmt, blob[i:i+step])
                except struct.error:
                    break
                ret.append(args)
            return zip(*ret)

    else:
        return [[] for _ in fmt.count('f')]

# ============= EOF =============================================
