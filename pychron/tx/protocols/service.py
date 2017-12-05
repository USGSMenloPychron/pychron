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
# ============= standard library imports ========================
import re
import traceback

from twisted.internet import defer
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver

from pychron.tx.errors import InvalidArgumentsErrorCode
from pychron.tx.exceptions import ServiceNameError, ResponseError
from pychron import json


def default_err(failure):
    print failure.getTraceback()
    failure.trap(BaseException)
    return failure


def service_err(failure):
    failure.trap(ServiceNameError)
    return failure


def response_err(failure):
    failure.trap(ResponseError)
    return failure


def nargs_err(failure):
    failure.trap(ValueError)
    return InvalidArgumentsErrorCode('Foo', str(failure.value))


# logger = Logger()

regex = re.compile(r'^(?P<command>\w+) {0,1}(?P<args>.*)')


class MockLogger(object):
    def __getattr__(self, item):
        def mockfunc(*args, **kw):
            pass

        return mockfunc


class ServiceProtocol(LineReceiver):
    def __init__(self, logger=None, *args, **kw):
        # super(ServiceProtocol, self).__init__(*args, **kw)
        self._services = {}
        self._cmd_delim = ' '
        self._arg_delim = ','

        if logger is None:
            logger = MockLogger()

        self.debug = logger.debug
        self.warning = logger.warn
        self.info = logger.info
        self.error = logger.error
        self.critical = logger.critical

    def dataReceived(self, data):
        self.debug('Received n={n}: {data!r}', n=len(data), data=data)
        data = data.strip()
        args = self._get_service(data)
        if args:
            service, data = args
            self._get_response(service, data)

    def register_service(self, service_name, success, err=None):
        """

        """

        if err is None:
            err = default_err

        d = defer.Deferred()
        if not isinstance(success, (list, tuple)):
            success = (success,)

        for si in success:
            d.addCallback(si)

        d.addCallback(self._prepare_response)
        d.addCallback(self._send_response)

        d.addErrback(nargs_err)
        d.addErrback(service_err)
        d.addErrback(err)

        self._services[service_name] = d

    def _register_services(self, services):
        for name, cb in services:
            if isinstance(cb, str):
                cb = getattr(self, cb)
            self.register_service(name, cb)

    def _prepare_response(self, data):
        if isinstance(data, bool) and data:
            return 'OK'
        elif data is None:
            return 'No Response'
        else:
            return data

    def _send_response(self, resp):
        resp = str(resp)
        self.debug('Response {data!r}', data=resp)
        self.transport.write(resp)
        self.transport.loseConnection()

    def _get_service(self, data):
        m = regex.match(data)
        if m:
            name = m.group('command')
            jd = data
        else:
            jd = json.loads(data)
            name = jd['command']

        try:
            service = self._services[name]
            return service, jd
        except KeyError, e:
            traceback.print_exc()
            raise ServiceNameError(name, data)

    def _prepare_data(self, data):
        if isinstance(data, dict):
            cdata = data
        else:
            delim = self._cmd_delim
            data = delim.join(data.split(delim)[1:])

            data = data.split(self._arg_delim)
            if len(data) == 1:
                data = data[0]
            else:
                data = tuple(data)
            cdata = data

        self.debug('Data {cdata!r}', cdata=cdata)
        return cdata

    def _get_response(self, service, data):
        cdata = self._prepare_data(data)
        service.callback(cdata)

# ============= EOF =============================================
# def sleep(secs):
# d = defer.Deferred()
#     reactor.callLater(secs, d.callback, None)
#     return d
