Usage on Travis CI
------------------

Hadoop-test-cluster works great on Travis CI. Here we provide a brief example
of one way to handle this.

.. code-block:: yaml

    before_install:
        - |
          set -xe

          # The docker-compose version on TravisCI currently is too old for
          # hadoop-test-cluster to work. Here we Upgrade docker-compose to a
          # newer version.
          sudo rm /usr/local/bin/docker-compose
          curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` > docker-compose
          chmod +x docker-compose
          sudo mv docker-compose /usr/local/bin

          # Install hadoop-test-cluster
          pip install hadoop-test-cluster

          # Start the test cluster, mounting your repository on the edge node.
          htcluster startup --mount .:your-repo-name

          set +xe

    install:
        - |
          set -xe

          # Install dependencies using conda
          htcluster exec -- conda install -y numpy pandas

          # Install dependencies using pip
          htcluster exec -- pip install pytest flake8

          # Build and install your package
          htcluster exec -- pip install -v -e ./your-repo-name

          set +xe

    script:
        # Run your test suite
        - htcluster exec -- py.test -vv your-repo-name


For real repositories running this on Travis CI, see the following examples:

- skein_
- dask-yarn_
- hdfscm_
- yarnspawner_
- filesystem_spec_


.. _skein: https://github.com/jcrist/skein/blob/master/.travis.yml
.. _dask-yarn: https://github.com/dask/dask-yarn/blob/master/.travis.yml
.. _yarnspawner: https://github.com/jcrist/yarnspawner/blob/master/.travis.yml
.. _hdfscm: https://github.com/jcrist/hdfscm/blob/master/.travis.yml
.. _filesystem_spec: https://github.com/martindurant/filesystem_spec/blob/master/.travis.yml
