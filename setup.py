from setuptools import setup

setup(name='hadoop-test-cluster',
      version='0.0.1',
      url="https://github.com/jcrist/hadoop-test-cluster",
      maintainer='Jim Crist',
      maintainer_email='jiminy.crist@gmail.com',
      license='BSD',
      description='A CLI for managing hadoop clusters for testing',
      long_description=open('README.md').read(),
      packages=['hadoop_test_cluster'],
      entry_points='''
        [console_scripts]
        hcluster=hadoop_test_cluster.cli:main
      ''',
      zip_safe=False)
