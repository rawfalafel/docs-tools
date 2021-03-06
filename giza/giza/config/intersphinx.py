# Copyright 2014 MongoDB, Inc.
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

import logging

logger = logging.getLogger('giza.config.helper')

from giza.config.base import ConfigurationBase

class IntersphinxConfig(ConfigurationBase):
    _option_registry = ['name']

    @property
    def url(self):
        return self.state['url']

    @url.setter
    def url(self, value):
        if value.startswith('http'):
            self.state['url'] = value
        else:
            raise TypeError

    @property
    def path(self):
        return self.state['path']

    @path.setter
    def path(self, value):
        if value.endswith('inv'):
            self.state['path'] = value
        else:
            raise TypeError
