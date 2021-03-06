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

import inspect
import logging
import os
import shutil

logger = logging.getLogger('giza.operations.quickstart')

import argh
import giza

from giza.config.helper import fetch_config
from giza.core.app import BuildApp
from giza.operations.sphinx import sphinx_publication
from giza.tools.command import command, CommandError

@argh.named('quickstart')
@argh.arg('--with-git', action='store_true', dest='quickstart_git')
def make_project(args):
    curdir = os.getcwd()
    curdir_list = os.listdir(curdir)

    _weak_bootstrapping(args)

    if args.quickstart_git is True:
        logger.info('creating a new git repository')
        r = command('git init', capture=True)

        if not r.out.startswith('Reinitialized'):
            command('git add .')
            try:
                command('git commit -m "initial commit"')
            except CommandError:
                pass

def _weak_bootstrapping(args):
    args.languages_to_build = args.editions_to_build = []
    args.builder = 'html'
    conf = fetch_config(args)
    app = BuildApp(conf)

    mod_path = os.path.dirname(inspect.getfile(giza))
    qstart_path = os.path.join(mod_path, 'quickstart')

    command('rsync --ignore-existing --recursive {0}/. {1}'.format(qstart_path, os.getcwd()))
    logger.info('migrated new site files')

    try:
        sphinx_publication(conf, args, app)
    except:
        sphinx_publication(conf, args, app)
        shutil.rmtree('docs-tools')

    command('python build/docs-tools/makecloth/meta.py build/makefile.meta')
    logger.info('bootstrapped makefile system')

    logger.info('updated project skeleton in current directory.')
