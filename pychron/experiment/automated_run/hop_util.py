# ===============================================================================
# Copyright 2014 Jake Ross
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


def parse_hop(args):
    if isinstance(args, dict):
        counts = args['counts']
        settle = args['settle']
        cc = args['cup_configuration']
        isos = [ci['isotope'] for ci in cc if ci.get('active', False)]
        dets = [ci['detector'] for ci in cc]
        defls = [ci.get('deflection') for ci in cc]
        pdets = [ci['detector'] for ci in cc if ci.get('protect', False)]
        is_baselines = [ci['is_baseline'] for ci in cc]
        active_detectors = [ci['detector'] for ci in cc if ci.get('active',False)]
        pos = args['positioning']

    else:
        if len(args) == 3:
            hopstr, counts, settle = args
            pdets = []
        else:
            hopstr, counts, settle, pdets = args
            # for hopstr, counts, settle, pdets in hops:
        is_baselines, isos, dets, defls = zip(*split_hopstr(hopstr))
        active_detectors = dets
        pos = {'detector': active_detectors[0], 'isotope': isos[0]}

    d = {'is_baselines': is_baselines,
         'isotopes': isos,
         'detectors': dets,
         'active_detectors': active_detectors,
         'deflections': defls,
         'settle': settle, 'counts': counts,
         'protect_detectors': pdets,
         'positioning': pos}

    return d


def generate_hops(hops):
    # for c in xrange(self.ncycles):
    c = 0
    while 1:
        for i, args in enumerate(hops):
            d = parse_hop(args)
            d['idx'] = i
            d['cycle'] = c
            d['is_baseline'] = is_baseline = any(d['is_baselines'])
            if is_baseline:
                yield d
                # yield c, is_baselines, dets, isos, defls, settle, counts
            else:
                for i in xrange(int(d['counts'])):
                    d['count'] = i
                    yield d
                    # yield c, is_baselines, dets, isos, defls, settle, i, pdets
        c += 1


def parse_hops(hops, ret=None):
    """
        hops list of hop tuples
        ret: comma-delimited str. valid values are ``iso``, ``det``, ``defl``
             eg. "iso,det"
    """
    for args in hops:
        # if len(args) == 3:
        #     hopstr, counts, settle = args
        # else:
        #     hopstr, counts, settle, pdets = args
        #
        # for is_baseline, iso, det, defl in split_hopstr(hopstr):

        d = parse_hop(args)
        counts, settle = d['counts'], d['settle']

        for is_baseline, iso, det, defl in zip(d['is_baselines'],
                                               d['isotopes'],
                                               d['active_detectors'],
                                               d['deflections']):
            if ret:
                loc = locals()
                r = [loc[ri.strip()] for ri in ret.split(',')]
                yield r
            else:
                yield is_baseline, iso, det, defl, counts, settle


def split_hopstr(hop):
    for hi in hop.split(','):
        args = map(str.strip, hi.split(':'))
        defl = None
        is_baseline = False
        if len(args) == 4:
            # this is a baseline
            _, iso, det, defl = args
            is_baseline = True
        elif len(args) == 3:
            iso, det, defl = args
            if iso == 'bs':
                is_baseline = True
                iso = det
                det = defl
                defl = None
        else:
            iso, det = args

        yield is_baseline, iso, det, defl

# ============= EOF =============================================
