import sys
import os.path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('makecloth.giza')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))

from makecloth import MakefileCloth

try:
    import giza
    from giza.config.helper import new_config
    from giza.tools.serialization import ingest_yaml_doc
    from giza.tools.strings import hyph_concat
except ImportError as e:
    giza = None
    print(e)

def build_makefile(m, conf):
    m.section_break('giza build integration')
    m.newline()

    m.section_break('content generation targets')
    for gen_target in [ 'api', 'assets', 'images', 'intersphinx', 'options',
                        'primer', 'steps', 'tables', 'toc']:
        m.target([gen_target, hyph_concat('giza', gen_target)])
        m.job('giza generate ' + gen_target)

        m.target([hyph_concat('force', gen_target), hyph_concat('giza', 'force', gen_target)])
        m.job('giza --force generate ' + gen_target)
        m.newline()

    m.section_break('sphinx targets')

    sconf = ingest_yaml_doc(os.path.join(conf.paths.projectroot,
                                         conf.paths.builddata,
                                         'sphinx.yaml'))
    builders = [b for b in sconf
                if not b.endswith('base') and b not in
                ('prerequisites', 'generated-source', 'languages', 'editions', 'sphinx_builders')]
    if 'editions' in sconf:
        editions = sconf['editions']
    else:
        editions = []

    if 'root-base' in sconf and 'languages' in sconf['root-base']:
        languages = sconf['root-base']['languages']
    else:
        languages = []

    complete = []

    for builder in builders:
        if '-' in builder:
            builder = builder.split('-')[0]

        if builder in complete:
            continue

        m.comment(builder + ' targets')
        for edition in editions:
            m.target([hyph_concat(builder, edition), hyph_concat('giza', builder, edition)])
            m.job('giza sphinx --builder {0} --edition {1}'.format(builder, edition))

            for language in languages:
                m.target([hyph_concat(builder, edition, language),
                          hyph_concat('giza', builder, edition, language)])
                m.job('giza sphinx --builder {0} --edition {1} --language {2}'.format(builder, edition, language))

        if len(editions) == 0:
            m.target([hyph_concat(builder),
                      hyph_concat('giza', builder)])
            m.job('giza sphinx --builder ' + builder)

            for language in languages:
                m.target([hyph_concat(builder, language),
                          hyph_concat('giza', builder, language)])
                m.job('giza sphinx --builder {0} --language {1}'.format(builder, language))
        else:
            m.target([hyph_concat(builder),
                      hyph_concat('giza', builder)])
            m.job('giza sphinx --builder {0} --edition {1}'.format(builder, ' '.join(editions)))

        m.newline()
        complete.append(builder)

    m.section_break('deploy targets')
    if 'push' in conf.system.files.data:
        for ptarget in conf.system.files.data.push:
            name = ptarget['target']
            m.target(hyph_concat('deploy', name))
            m.job('giza deploy --target ' + name)
            m.newline()

    m.section_break('integration and publish targets')

    m.target(['giza-publish', 'publish'])

    base_job = 'giza sphinx --builder publish'
    if len(editions) > 0:
        base_job += " --serial_sphinx --edition " + ' '.join(editions)

    m.job(base_job)
    m.newline()

    for lang in languages:
        m.target([hyph_concat('publish', lang),
                  hyph_concat('giza', 'publish', lang)])
        m.job(base_job + ' --language ' + lang)
        m.newline()

    # following targets build a group of sphinx targets followed by running
    # one or more deploy actions.
    m.section_break('push targets')
    if 'push' in conf.system.files.data:
        for ptarget in conf.system.files.data.push:
            push_base_job = 'giza push --deploy {0} --builder publish'.format(ptarget['target'])

            if len(editions) > 0:
                push_base_job += " --serial_sphinx --edition " + ' '.join(editions)

            m.target([ptarget['target'],
                      hyph_concat('giza', ptarget['target'])])
            m.job(push_base_job)
            m.newline()

            for lang in languages:
                m.target([ hyph_concat(ptarget['target'], lang),
                           hyph_concat('giza', ptarget['target'], lang) ])
                m.job(push_base_job + ' --language ' + lang)
                m.newline()

    return m

def main():
    m = MakefileCloth()
    conf = new_config()
    output_file = os.path.join(conf.paths.projectroot, conf.paths.output, 'makefile.giza_build')

    m = build_makefile(m, conf)

    m.write(output_file)
    print('[meta-build]: built "build/makefile.giza_build" to integrate giza')

if __name__ == '__main__':
    if giza is None:
        logger.warning('giza is not available. not generating makefile.')
    else:
        main()
