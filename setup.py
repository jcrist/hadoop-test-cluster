from setuptools import setup

import os
import shutil

# Copy the krb5.conf file into the source tree if necessary
_this_dir = os.path.abspath(os.path.dirname(os.path.relpath(__file__)))
krb5_conf = os.path.join(_this_dir, 'images', 'hadoop-testing-kerberos',
                         'files', 'etc', 'krb5.conf')
krb5_target = os.path.join(_this_dir, 'hadoop_test_cluster', 'krb5.conf')
if os.path.exists(krb5_conf):
    shutil.copyfile(krb5_conf, krb5_target)


setup(name='hadoop-test-cluster',
      version='0.0.5',
      url="https://github.com/jcrist/hadoop-test-cluster",
      maintainer='Jim Crist',
      maintainer_email='jiminy.crist@gmail.com',
      license='BSD',
      description='A CLI for managing hadoop clusters for testing',
      long_description=open('README.rst').read(),
      packages=['hadoop_test_cluster'],
      package_data={'hadoop_test_cluster': ['docker-compose.yaml',
                                            'krb5.conf']},
      entry_points='''
        [console_scripts]
        htcluster=hadoop_test_cluster.cli:main
      ''',
      zip_safe=False)
