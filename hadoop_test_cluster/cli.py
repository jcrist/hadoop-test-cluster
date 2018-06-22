from __future__ import print_function, division, absolute_import

import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback
from contextlib import contextmanager


__version__ = '0.0.1'


_this_dir = os.path.abspath(os.path.dirname(os.path.relpath(__file__)))
COMPOSE_FILE = os.path.join(_this_dir, 'docker-compose.yaml')
KRB5_CONF = os.path.join(_this_dir, 'krb5.conf')


MAP_DIRECTORY_TEMPLATE = """
version: "3.5"

services:
  edge:
    volumes:
"""


def dispatch_and_exit(command, env=None):
    environ = dict(os.environ)
    environ.update(env)
    proc = subprocess.Popen(' '.join(command), env=environ, shell=True)
    sys.exit(proc.wait())


class _VersionAction(argparse.Action):
    def __init__(self, option_strings, version=None, dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS, help="Show version then exit"):
        super(_VersionAction, self).__init__(option_strings=option_strings,
                                             dest=dest, default=default,
                                             nargs=0, help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        print(self.version % {'prog': parser.prog})
        sys.exit(0)


def fail(msg, prefix=True):
    if prefix:
        msg = 'Error: %s' % msg
    print(msg, file=sys.stderr)
    sys.exit(1)


def add_help(parser):
    parser.add_argument("--help", "-h", action='help',
                        help="Show this help message then exit")


def arg(*args, **kwargs):
    return (args, kwargs)


def subcommand(subparsers, name, help, *args):
    def _(func):
        parser = subparsers.add_parser(name,
                                       help=help,
                                       description=help,
                                       add_help=False)
        parser.set_defaults(func=func)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        add_help(parser)
        func.parser = parser
        return func
    return _


def node(subs, name, help):
    @subcommand(subs, name, help)
    def f():
        fail(f.parser.format_usage(), prefix=False)
    f.subs = f.parser.add_subparsers(metavar='command', dest='command')
    f.subs.required = True
    return f


@contextmanager
def map_directories(directories):
    if directories:
        mapping = {}
        for d in directories:
            parts = d.rsplit(':', 1)
            if len(parts) == 1:
                fail("Working directories must be provided in "
                     "``source:target`` format, got %r" % d)

            source, target = parts

            if '/' in target:
                fail("target's must be a single directory")
            elif target in mapping:
                fail("target %r provided multiple times" % target)
            elif not os.path.isdir(source):
                fail("Directory %r doesn't exist" % source)

            mapping[target] = os.path.abspath(source)

        volumes = ['%s:/home/testuser/%s' % (s, t) for t, s in mapping.items()]

        overlay = {'version': '3.5',
                   'services': {'edge': {'volumes': volumes}}}

        handle, filename = tempfile.mkstemp('.json')

        with os.fdopen(handle, 'w') as fil:
            json.dump(overlay, fil)

        try:
            yield ['-f', filename]
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    else:
        yield []


htcluster = argparse.ArgumentParser(prog="htcluster",
                                    description="Manage hadoop test clusters",
                                    add_help=False)
add_help(htcluster)
htcluster.add_argument("--version", action=_VersionAction,
                       version='%(prog)s ' + __version__,
                       help="Show version then exit")
htcluster.set_defaults(func=lambda: fail(htcluster.format_usage(), prefix=False))
htcluster_subs = htcluster.add_subparsers(metavar='command', dest='command')
htcluster_subs.required = True

kind = arg('--kind', default='base',
           help=('The kind of hadoop cluster to start. Either `base` or '
                 '`kerberos`'))
user = arg("--user", "-u", default='testuser',
           help="The user to login as. Default is 'testuser'.")
service = arg("--service", "-s", default="edge",
              help="The service to login to. Default is 'edge'.")
cmd = arg('cmd', nargs='+', help="The command to execute")


def parse_kind(kind):
    if kind == 'base':
        return 'jcrist/hadoop-testing-base'
    elif kind == 'kerberos':
        return 'jcrist/hadoop-testing-kerberos'
    else:
        fail("--kind must be either `base` or `kerberos`")


@subcommand(htcluster_subs,
            'startup', 'Start up a hadoop cluster.',
            kind,
            arg('--mount', '-m', action='append',
                help=('Mount directory `source` to `~/dest` by passing '
                      '`--mount source:dest`. May be passed multiple times')))
def htcluster_startup(kind, mount=()):
    kind = kind.lower()
    image = parse_kind(kind)

    env = dict(HADOOP_TESTING_FIXUID=str(os.getuid()),
               HADOOP_TESTING_FIXGID=str(os.getgid()),
               HADOOP_TESTING_IMAGE=image)

    command = ['docker-compose', '-f', COMPOSE_FILE]
    with map_directories(mount) as extra_args:
        command.extend(extra_args)
        command.extend(['up', '-d'])
        print("Starting a %s cluster..." % kind)
        dispatch_and_exit(command, env)


@subcommand(htcluster_subs,
            'login', "Login to a node in the cluster.",
            user,
            service)
def htcluster_login(user, service):
    env = dict(HADOOP_TESTING_IMAGE='jcrist/hadoop-testing-base')
    command = ['docker-compose', '-f', COMPOSE_FILE,
               'exec', '-u', user, service,
               'bash', '--init-file', '/root/init-shell.sh']
    dispatch_and_exit(command, env)


@subcommand(htcluster_subs,
            'exec', "Execute a command on the node as a user",
            user, service, cmd)
def htcluster_exec(user, service, cmd=None):
    env = dict(HADOOP_TESTING_IMAGE='jcrist/hadoop-testing-base')
    command = ['docker-compose', '-f', COMPOSE_FILE,
               'exec', '-u', user, service,
               '/root/run_command.sh']
    command.extend(cmd)
    dispatch_and_exit(command, env)


@subcommand(htcluster_subs,
            'shutdown', "Shutdown the cluster and remove the containers.")
def htcluster_shutdown():
    env = dict(HADOOP_TESTING_IMAGE='jcrist/hadoop-testing-base')
    command = ['docker-compose', '-f', COMPOSE_FILE, 'down']
    print("Shutting down cluster...")
    dispatch_and_exit(command, env)


@subcommand(htcluster_subs,
            'compose',
            "Forward commands to docker-compose",
            kind, cmd)
def htcluster_compose(kind, cmd):
    image = parse_kind(kind.lower())
    env = dict(HADOOP_TESTING_IMAGE=image)
    command = ['docker-compose', '-f', COMPOSE_FILE]
    command.extend(cmd)
    dispatch_and_exit(command, env)


@subcommand(htcluster_subs,
            'kerbenv',
            ("Output environment variables to setup kerberos locally.\n\n"
             "Intended use is to eval the output in bash:\n\n"
             "eval $(htcluster kerbenv)"))
def htcluster_kerbenv():
    print("export KRB5_CONFIG='%s'" % KRB5_CONF)


def main(args=None):
    kwargs = vars(htcluster.parse_args(args=args))
    kwargs.pop('command', None)  # Drop unnecessary `command` arg
    func = kwargs.pop('func')
    try:
        func(**kwargs)
    except Exception:
        fail("Unexpected Error:\n%s" % traceback.format_exc(), prefix=False)
    sys.exit(0)


if __name__ == '__main__':
    main()
