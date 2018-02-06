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

# ============= standard library imports ========================

# ============= local library imports  ==========================
import math

"""
    http://stackoverflow.com/questions/10991991/pyside-easier-way-of-updating-gui-from-another-thread
"""
#
#
# class InvokeEvent(QtCore.QEvent):
#     EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
#
#     def __init__(self, fn, *args, **kwargs):
#         QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
#         self.fn = fn
#         self.args = args
#         self.kwargs = kwargs
#
#
# class Invoker(QtCore.QObject):
#     def event(self, event):
#         event.fn(*event.args, **event.kwargs)
#         return True
#
#
# _invoker = Invoker()
#
# def invoke_in_main_thread(fn, *args, **kwargs):
#     QtCore.QCoreApplication.postEvent(_invoker, InvokeEvent(fn, *args, **kwargs), QtCore.Qt.NormalEventPriority)
#     QtCore.QCoreApplication.sendPostedEvents(_invoker)
#     QtCore.QCoreApplication.processEvents()


# def invoke_in_main_thread(fn, *args, **kw):
#     from pyface.gui import GUI
#     GUI.invoke_later(fn, *args,  **kw)


def convert_color(color, output='rgbF'):
    from pyface.qt.QtGui import QColor

    if isinstance(color, QColor):
        rgb = color.red(), color.green(), color.blue()

    tofloat = lambda x: x / 255.
    if output == 'rgbF':
        return map(tofloat, rgb[:3])
    elif output == 'rgbaF':
        return map(tofloat, rgb)


def wake_screen():
    import random, time
    from pyface.qt.QtGui import QCursor

    time.sleep(5)

    q = QCursor()
    pos = q.pos()
    ox, oy = pos.x(), pos.y()

    def rgen():
        r = 300
        while 1:
            theta = math.radians(random.random() * 360)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            yield ox + x, oy + y

    random_point = rgen()

    for i in range(5):
        x, y = random_point.next()
        q.setPos(x, y)
        time.sleep(0.1)
    q.setPos(ox, oy)


# ============= EOF =============================================
