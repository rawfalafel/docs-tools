import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.files import expand_tree
from utils.git import get_branch
from utils.serialization import ingest_yaml
from utils.config import get_conf, get_conf_file

from makecloth import MakefileCloth

try:
    site_conf = get_conf()
except:
    from giza.config.helper import fetch_config
    from giza.config.runtime import RuntimeStateConfig
    site_conf = fetch_config(RuntimeStateConfig())

conf = site_conf

m = MakefileCloth()
paths = site_conf.paths

def generate_integration_targets(conf):
    m.target('_publish')
    base = 'fab'
    if site_conf.project.name == 'ecosystem':
        base += ' serial'

    m.job('{0} sphinx.target:{1}'.format(base, ','.join(conf['targets'])))

    m.target('_publish-debug')
    m.job('{0} log.set:debug sphinx.target:{1}'.format(base, ','.join(conf['targets'])))

    dependencies = [ '_publish']
    dependencies_debug = [ '_publish-debug']

    if 'doc_root' in conf:
        for dep in conf.doc_root:
            dependencies.append(os.path.join(paths.public, dep))
            dependencies_debug.append(os.path.join(paths.public, dep))

    dependencies.extend(proccess_branch_root(conf))
    dependencies_debug.extend(proccess_branch_root(conf))

    m.target('publish', dependencies)
    m.msg('[build]: deployed branch {0} successfully to {1}'.format(get_branch(), paths.public))
    m.newline()

    m.target('publish-debug', dependencies_debug)
    m.msg('[build]: deployed branch {0} successfully to {1}'.format(get_branch(), paths.public))
    m.newline()

    m.target('package')
    m.job('fab stage.package')
    m.target('package-debug')
    m.job('fab log.set:debug stage.package')

    m.target('.PHONY', ['_publish', 'publish', 'package'])

def proccess_branch_root(conf):
    dependencies = []

    if 'branch_root' in conf and conf.branch_root is not None:
        for dep in conf.branch_root:
            if isinstance(dep, list):
                dep = os.path.sep.join(dep)

            if dep != '':
                dependencies.append(os.path.join(paths.branch_staging, dep))
            else:
                dependencies.append(paths.branch_staging)

    return dependencies

def gennerate_translation_integration_targets(language, conf):
    dependencies = [ l + '-' + language for l in conf['targets'] ]
    dependencies_debug = [ dep + "-debug" for dep in dependencies ]

    for dep in conf['doc-root']:
        dependencies.append(os.path.join(paths.public, dep))

    dependencies.extend(proccess_branch_root(conf))

    package_target = '-'.join(['package', language])
    publish_target = '-'.join(['publish', language])

    m.target(package_target)
    m.job('fab stage.package:' + language)

    m.target(package_target + '-debug')
    m.job('fab log.set:debug stage.package:' + language)

    m.target(publish_target + '-debug', dependencies_debug)

    m.target(publish_target)
    m.job('fab sphinx.target:{0}'.format(','.join(dependencies)))
    m.msg('[build]: deployed branch {0} successfully to {1}'.format(get_branch(), paths.public))
    m.newline()

    m.target('.PHONY', [publish_target + '-debug', package_target + '-debug', publish_target, package_target])

def main():
    fn = sys.argv[1]

    if os.path.isfile(fn):
        os.remove(fn)

    # conf_file = get_conf_file(__file__, conf=conf)

    # config = ingest_yaml(conf_file)

    # if 'base' in config:
    #     generate_integration_targets(config['base'])

    #     for lang, lang_config in config.items():
    #         if lang == 'base':
    #             continue

    #         if 'inherit' in lang_config:
    #             new_config = config[lang_config['inherit']]
    #             new_config.update(lang_config)

    #             gennerate_translation_integration_targets(lang, new_config)
    #         else:
    #             gennerate_translation_integration_targets(lang, lang_config)
    # else:
    #     generate_integration_targets(config)

    # m.write(sys.argv[1])
    # print('[meta-build]: build "' + sys.argv[1] + '" to specify integration targets.')

if __name__ == '__main__':
    main()
