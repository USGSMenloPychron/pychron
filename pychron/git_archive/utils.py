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
from datetime import datetime

import re
from git import Repo, Blob, Diff
from gitdb.util import hex_to_bin
from traits.api import HasTraits, Str, Bool, Date


# ============= local library imports  ==========================

TAG_RE = re.compile(r'^\<\w+\>')


class GitShaObject(HasTraits):
    message = Str
    date = Date
    blob = Str
    name = Str
    hexsha = Str
    author = Str
    email = Str
    active = Bool
    tag = Str


def from_gitlog(obj, path, tag=None):
    hexsha, author, email, ct, message = obj.split('|')
    date = datetime.fromtimestamp(float(ct))

    if tag is None:
        tag = TAG_RE.match('message')
        if tag:
            tag = tag.group('tag')
        else:
            tag = 'NULL'

    g = GitShaObject(hexsha=hexsha,
                     message=message,
                     date=date,
                     author=author,
                     email=email,
                     path=path,
                     tag=tag)
    return g


def gitlog(repo, branch=None, args=None, path=None):
    cmd = []
    if branch:
        cmd.append(branch)

    fmt = '%H|%cn|%ce|%ct|%s'
    cmd.append('--pretty={}'.format(fmt))

    if args:
        cmd.extend(args)

    if path:
        cmd.extend(['--', path])
    return repo.git.log(*cmd)


def get_head_commit(repo):
    txt = gitlog(repo, args=('-n', '1', 'HEAD'))
    return from_gitlog(txt.strip(), '', '')


def get_commits(repo, branch, path, tag, *args):
    if isinstance(repo, (str, unicode)):
        if not os.path.isdir(repo):
            return
        repo = Repo(repo)

    txt = gitlog(repo, branch=branch, args=args, path=path)

    return [from_gitlog(l.strip(), path, tag) for l in txt.split('\n')] if txt else []


def get_log(repo, branch, path):
    if isinstance(repo, (str, unicode)):
        if not os.path.isdir(repo):
            return
        repo = Repo(repo)

    return gitlog(repo, branch=branch, path=path)


def get_repo(repo):
    if isinstance(repo, (str, unicode)):
        if not os.path.isdir(repo):
            return
        repo = Repo(repo)

    return repo


def get_diff(repo, a, b, path, change_type='M'):
    repo = get_repo(repo)
    diff = repo.git.diff(a, b, '--full-index', '--', path)
    if diff:
        return fu(repo, diff)


aregex = re.compile(r'\[ahead (?P<count>\d+)')
bregex = re.compile(r'behind (?P<count>\d+)')


def ahead_behind(repo, fetch=True, remote='origin'):
    repo = get_repo(repo)

    ahead = 0
    behind = 0
    if fetch:
        repo.git.fetch(remote)

    status = repo.git.status('-sb')

    ma = aregex.search(status)
    mb = bregex.search(status)
    if ma:
        ahead = int(ma.group('count'))
    if mb:
        behind = int(mb.group('count'))

    return ahead, behind


def fu(repo, text):
    for header in Diff.re_header.finditer(text):
        groups = header.groups()

        a_path_fallback = groups[0]
        b_path_fallback = groups[1]
        old_mode = groups[2]
        new_mode = groups[3]
        rename_from = groups[4]
        rename_to = groups[5]
        new_file_mode = groups[6]
        deleted_file_mode = groups[7]
        a_blob_id = groups[8]
        b_blob_id = groups[9]
        b_mode = groups[10]
        a_path = groups[11]
        b_path = groups[12]

        # print groups
        # print len(groups)
        # a_path, b_path, \
        # similarity_index, rename_from, rename_to, \
        # old_mode, new_mode, new_file_mode, deleted_file_mode, \
        # a_blob_id, b_blob_id, b_mode = header.groups()

        # new_file, deleted_file = bool(new_file_mode), bool(deleted_file_mode)

        # Our only means to find the actual text is to see what has not been matched by our regex,
        # and then retro-actively assin it to our index
        # if previous_header is not None:
        #     index[-1].diff = text[previous_header.end():header.start()]
        # end assign actual diff

        # Make sure the mode is set if the path is set. Otherwise the resulting blob is invalid
        # We just use the one mode we should have parsed
        a_mode = old_mode or deleted_file_mode or (a_path and (b_mode or new_mode or new_file_mode))
        b_mode = b_mode or new_mode or new_file_mode or (b_path and a_mode)
        ablob = Blob(repo, hex_to_bin(a_blob_id), mode=a_mode, path=a_path)
        bblob = Blob(repo, hex_to_bin(b_blob_id), mode=b_mode, path=a_path)
        return ablob, bblob


if __name__ == '__main__':
    repo = '/Users/ross/Pychron_dev/data/.dvc/experiments/J-Curve'
    # for c in get_commits(repo, 'master', 'a-01/tag/-J-2562.tag.json', '--grep=^Update'):
    #     print c.hexsha, c.date, c.message
    # get_diff(repo, 'HEAD', '0ed461408fc8939909a907a73d2d991efc334eec')
    # get_diff(repo, '0ed461408fc8939909a907a73d2d991efc334eec', 'HEAD')
    get_diff(repo, 'HEAD~1', 'HEAD')

# ============= EOF =============================================
