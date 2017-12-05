# ===============================================================================
# Copyright 2011 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# =============enthought library imports=======================
import os
import shutil
import time
from threading import Thread, Lock, Event

from PIL import Image as PImage
from numpy import asarray
from traits.api import Any, Bool, Float, List, Str, Int

from cv_wrapper import get_capture_device
from pychron.core.helpers.filetools import add_extension
from pychron.globals import globalv
from pychron.image.image import Image


def convert_to_video(path, fps, name_filter='snapshot%03d.jpg',
                     ffmpeg=None,
                     output=None):
    """
        path: path to directory containing list of images

        commandline
        $ ffmpeg -r 25 -codec x264 -i /snapshot%03d.jpg -o output.avi


    """
    import subprocess
    if output is None:
        output = os.path.join(path, '{}.avi'.format(path))

    if os.path.exists(output):
        return

    frame_rate = str(fps)
    # codec = '{}'.format('x264')  # H.264
    path = str(os.path.join(path, name_filter))
    if ffmpeg is None or not os.path.isfile(ffmpeg):
        ffmpeg = '/usr/local/bin/ffmpeg'

    # print 'calling {}, frame_rate={} '.format(ffmpeg, frame_rate)
    call_args = [ffmpeg, '-r', frame_rate, '-i', path, output]
    print ' '.join(call_args)

    subprocess.call(call_args)


def pil_save(src, p, ext='.jpg'):
    im = PImage.fromarray(src)
    p = add_extension(p, ext=ext)
    im.save(p)


class Video(Image):
    """
    class for accessing a streaming camera.
    """
    cap = Any
    track_mouse = Bool
    mouse_x = Float
    mouse_y = Float

    users = List

    _recording = Bool(False)
    _lock = None
    _prev_frame = None
    _stop_recording_event = None
    _save_ok_event = None
    _last_get = None

    output_path = Str
    output_mode = Str('MPEG')
    ffmpeg_path = Str
    fps = Int

    def is_recording(self):
        return self._recording

    def is_open(self):
        return self.cap is not None

    def open(self, user=None, identifier=0, force=False):
        """
        get a camera/capture device

        """
        self._lock = Lock()
        self.width = 640
        self.height = 480
        if self.cap is None or force:

            if globalv.video_test:
                self.cap = 1
            else:

                if isinstance(identifier, str) and identifier.startswith('pvs'):
                    self.cap = self._get_remote_device(identifier)
                    # identifier is a url
                else:
                    # ideally an identifier is passed in
                    try:
                        self.cap = get_capture_device()
                        self.cap.open(int(identifier) if identifier else 0)
                    except Exception, e:
                        print 'video.open', e
                        self.cap = None

        if user not in self.users:
            self.users.append(user)

    def close(self, user=None, force=False):
        """
            remove user for user list.

            if user list is empty release/close the capture device
        """
        if force and self.cap:
            if not isinstance(self.cap, int):
                self.cap.release()
            self.cap = None
            return

        if user in self.users:
            i = self.users.index(user)
            self.users.pop(i)
            if not self.users:
                if self.cap is not None:
                    self.cap.release()
                self.cap = None

    def get_image_data(self, cmap=None, **kw):
        frame = self.get_frame(**kw)
        return asarray(frame)
        # if frame is not None:
        #     return asarray(frame[:, :])

    def start_recording(self, path, renderer=None):
        self._stop_recording_event = Event()
        self.output_path = path

        fps = 12
        if self.cap is None:
            self.open()

        if self.cap is not None:
            self._recording = True

            t = Thread(target=self._ffmpeg_record, args=(path, self._stop_recording_event,
                                                         fps, renderer))
            t.start()

    def stop_recording(self, wait=False):
        """
        """
        if self._stop_recording_event is not None:
            self._stop_recording_event.set()
        self._recording = False
        if wait:
            self._save_ok_event = Event()
            return self._ready_to_save()

    def record_frame(self, path, crop=None, **kw):
        """
        """
        src = self.get_frame(**kw)
        if src is not None:
            self.save(path, src=src)

        return src.clone()

    # private
    def _ready_to_save(self, timeout=120):
        if self._save_ok_event:
            st = time.time()
            while not self._save_ok_event.is_set():
                time.sleep(0.5)
                if timeout and time.time()-st>timeout:
                    return

            return True

    def _ffmpeg_record(self, path, stop, fps, renderer=None):
        """
            use ffmpeg to stitch a directory of jpegs into a video

        """
        remove_images = False
        root = os.path.dirname(path)
        name = os.path.basename(path)
        name, _ext = os.path.splitext(name)

        image_dir = os.path.join(root, '{}-images'.format(name))
        cnt = 0
        while os.path.exists(image_dir):
            image_dir = os.path.join(root, '{}-images-{:03d}'.format(name, cnt))
            cnt += 1

        os.mkdir(image_dir)

        cnt = 0

        if renderer is None:
            def renderer(p):
                frame = self.get_cached_frame()
                if frame is not None:
                    pil_save(frame, p)

                    # self.save(p, frame)
        # else:
        #     save = lambda x: renderer(x)

        fps_1 = 1 / float(fps)
        # with consumable(func=save) as con:
        #     while not stop.is_set():
        #         st = time.time()
        #         pn = os.path.join(image_dir, 'image_{:05d}.jpg'.format(cnt))
        #         con.add_consumable(pn)
        #         cnt += 1
        #         dur = time.time() - st
        #         time.sleep(max(0, fps_1 - dur))
        while not stop.is_set():
            st = time.time()
            pn = os.path.join(image_dir, 'image_{:05d}.jpg'.format(cnt))

            renderer(pn)
            # con.add_consumable(pn)
            cnt += 1
            dur = time.time() - st
            time.sleep(max(0, fps_1 - dur))

        self._convert_to_video(image_dir, fps, name_filter='image_%05d.jpg', output=path)

        if remove_images:
            shutil.rmtree(image_dir)

        if self._save_ok_event:
            self._save_ok_event.set()

    def _get_remote_device(self, url):
        from pychron.image.video_source import VideoSource
        vs = VideoSource()
        vs.set_url(url)
        vs.on_trait_change(self._update_fps, 'fps')

        return vs

    def _update_fps(self, fps):
        print 'update fps', fps
        self.fps = fps

    def _get_frame(self, lock=True, **kw):
        cap = self.cap
        if globalv.video_test:
            p = globalv.video_test_path
            self.load(p, swap_rb=True)

            f = self.source_frame
            return f

        elif cap is not None:
            s, img = self.cap.read()
            if s:
                return img

    def _convert_to_video(self, path, fps, name_filter='snapshot%03d.jpg', output=None):
        print 'convert to video. FFmpeg={}'.format(self.ffmpeg_path)

        ffmpeg = self.ffmpeg_path
        convert_to_video(path, fps, name_filter, ffmpeg, output)

# =================== EOF =================================================
