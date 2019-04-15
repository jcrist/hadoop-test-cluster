hadoop-test-cluster
===================

This package provides a docker setup and command-line tool for setting up and
managing several realistic Hadoop_ clusters. These can be useful for demo
purposes, but their main intended use is development and *testing*. The Hadoop
documentation is pretty emphatic about the `need for testing
<https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YarnApplicationSecurity.html#Important>`__:

.. 

    *If you don’t test your YARN application in a secure Hadoop cluster, it
    won’t work.*


Hadoop's security model is notoriously tricky to get correct. So hard, one of
the main contributors wrote `an online book`_ comparing its difficulties to
`Lovecraftian Horrors`_. The clusters provided here have settings selected to
hit potential issues in Hadoop and YARN applications so you can fix your code
early rather than in production. If your code runs on these clusters, it
should (hopefully) run on any cluster.

**Demo**

.. raw:: html

    <div align="center">
      <script src="https://asciinema.org/a/241014.js" id="asciicast-241014" async data-speed="3"></script>
    </div>

**Highlights**

- Easy to use `command-line tool <cli.html>`__
- Supports both Hadoop 2 (`CDH 5`_) and Hadoop 3 (`CDH 6`_)
- Supports both Kerberos_ and Simple authentication modes
- Comes with common development and testing dependencies pre-installed
  (miniconda_, maven_, git_, ...)
- Designed to minimize resource usage - runs fine both on laptops and on
  common CI servers such as `Travis CI <travis.html>`__
- Configured with a set of options designed to expose bugs in Hadoop
  applications. If your code runs on these clusters, it should (hopefully) run
  anywhere.

.. contents:: :local:

Installation
------------

``hadoop-test-cluster`` is available on PyPI:

.. code-block:: console

    $ pip install hadoop-test-cluster

You can also install from source on github:

.. code-block:: console

    $ pip install git+https://github.com/jcrist/hadoop-test-cluster.git


Docker_ and `Docker Compose`_ are required to already be installed on your
system - consult their docs for installation instructions.

Overview
--------

The main entry point for this package is the ``htcluster`` command-line tool.
This tool can be used to start, stop, and interact with test Hadoop clusters.

Startup a Cluster
^^^^^^^^^^^^^^^^^

To start a cluster, use the ``htcluster startup`` command. Two parameters are
used to describe which cluster to run:

- ``--image``: which docker image to use
- ``--config``: which Hadoop configuration to run the cluster with

**Images**

Currently supported images are:

- ``cdh5``: a `CDH 5`_ installation of Hadoop 2.6 (image at `jcrist/hadoop-testing-cdh5`_)
- ``cdh6``: a `CDH 6`_ installation of Hadoop 3.0 (image at `jcrist/hadoop-testing-cdh6`_)

To determine which version of Hadoop a cluster is running, see the
``HADOOP_TESTING_VERSION`` environment variable (will be set to either ``cdh5``
or ``cdh6``).

**Configurations**

Currently two different configurations are supported:

- ``simple``: uses simple authentication (unix user permissions)
- ``kerberos``: uses kerberos for authentication

To determine which configuration a cluster is running, see the
``HADOOP_TESTING_CONFIG`` environment variable (will be set to either
``simple`` or ``kerberos``).

**Examples**

Start a CDH 5 cluster with simple authentication:

.. code-block:: console

    $ htcluster startup --image cdh5 --config simple

Start a CDH6 cluster with kerberos authentication:

.. code-block:: console

    $ htcluster startup --image cdh6 --config kerberos


Start a cluster, mounting the current directory to ~/workdir:

.. code-block:: console

    $ htcluster startup --image cdh5 --mount .:workdir

Login to a Cluster
^^^^^^^^^^^^^^^^^^

For interactive work, you can log in to a cluster using the ``htcluster login``
command.

**Examples**

Login to the edge node as the default user:

.. code-block:: console

    $ htcluster login

Login to the master node as root:

.. code-block:: console

    $ htcluster login --user root --service master

Execute a Command on a Cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of logging in, you can also run a command on a cluster using the
``htcluster exec`` command.

**Examples**

Run ``py.test`` on a cluster:

.. code-block:: console

    $ htcluster exec -- py.test /path/to/my/tests

Follow the HDFS Namenode logs:

.. code-block:: console

    $ htcluster exec --user root --service master \
      -- tail -f /var/log/hadoop-hdfs/hadoop-hdfs-namenode.log

Shutdown a Cluster
^^^^^^^^^^^^^^^^^^

To shutdown a cluster, use the ``htcluster shutdown`` command.

**Example**

.. code-block:: console

    $ htcluster shutdown


Cluster Details
---------------

Here we provide more details on what each cluster supports.

Layout
^^^^^^

Each cluster has three containers:

- One ``master`` node running the ``hdfs-namenode`` and
  ``yarn-resourcemanager``, as well as the kerberos daemons. Hostname is
  ``master.example.com``.
- One ``worker`` node running the ``hdfs-datanode`` and ``yarn-nodemanager``.
  Hostname is ``worker.example.com``.
- One ``edge`` node for interacting with the cluster. Hostname is
  ``edge.example.com``.

Installed Packages
^^^^^^^^^^^^^^^^^^

All clusters provide the following packages:

- HDFS
- YARN
- Kerberos_
- Miniconda_
- Maven_
- Git_

Additional packages can be installed at runtime with ``yum``, ``conda``, or
``pip``.

Users
^^^^^

One default user account has also been created for testing purposes:

- Login: ``testuser``
- Password: ``testpass``

When using kerberos, a keytab for this user has been put at
``/home/testuser/testuser.keytab``, so you can kinit easily like ``kinit -kt
/home/testuser/testuser.keytab testuser``.

An admin kerberos principal has also been created for use with ``kadmin``:

- Login: ``root/admin``
- Password: ``adminpass``

Ports
^^^^^

The following ports are exposed:

**Master Node**

- NameNode RPC: 9000
- NameNode Webui: 50070
- ResourceManager Webui: 8088
- Kerberos KDC: 88
- Kerberos Kadmin: 749

**Worker Node**
- DataNode Webui: 50075
- NodeManager Webui: 8042

**Edge Node**
- User Defined: 8888
- User Defined: 8786

The full address for accessing these is dependent on the IP address of your
docker-machine driver, which can be found at:

.. code-block:: console

    $ docker-machine inspect --format {{.Driver.IPAddress}})

If you frequently want access to the WebUI's, it's recommended to add the
following lines to your ``/etc/hosts``:

.. code-block:: text

    <docker-machine-ip>    edge.example.com
    <docker-machine-ip>    master.example.com
    <docker-machine-ip>    worker.example.com


Authenticating with Kerberos from outside Docker
------------------------------------------------

With the kerberos configuration, the Web UI's are secured by kerberos, and so
won't be accessible from your browser unless you configure things properly.
This is doable, but takes a few steps:

1. Kerberos/SPNEGO requires that the requested url matches the hosts domain.
   The easiest way to do this is to modify your ``/etc/hosts`` and add a line for
   ``master.example.com``:

   .. code-block:: console

      # Add a line to /etc/hosts pointing master.example.com to your docker-machine
      # driver ip address.
      # Note that you probably need to run this command as a super user.
      $ echo "$(docker-machine inspect --format {{.Driver.IPAddress}})  master.example.com" >> /etc/hosts

2. You must have ``kinit`` installed locally. You may already have it, otherwise
   it's available through most package managers.

3. You need to tell kerberos where the ``krb5.conf`` is for this domain. This is
   done with an environment variable. To make this easy, ``htcluster`` has a
   command to do this:

   .. code-block:: console

      $ eval $(htcluster kerbenv)

4. At this point you should be able to kinit as testuser:

   .. code-block:: console

      $ kinit testuser@EXAMPLE.COM

5. To access kerberos secured pages in your browser you'll need to do a bit of
   (simple) configuration. See `this documentation from Cloudera`_ for
   information on what's needed for your browser.

6. Since environment variables are only available for processes started in the
   environment, you have three options here:

   - Restart your browser from the shell in which you added the environment
     variables

   - Manually get a ticket for the ``HTTP/master.example.com`` principal. Note
     that this will delete your other tickets, but works fine if you just want
     to see the webpage

     .. code-block:: console

        $ kinit -S HTTP/master.example.com testuser

   - Use ``curl`` to authenticate the first time, at which point you'll already
     have the proper tickets in your cache, and the browser authentication will
     just work. Note that your version of curl must support the GSS-API.

     .. code-block:: console

        $ curl -V  # Check your version of curl supports GSS-API
        curl 7.59.0 (x86_64-apple-darwin17.2.0) libcurl/7.59.0 SecureTransport zlib/1.2.11
        Release-Date: 2018-03-14
        Protocols: dict file ftp ftps gopher http https imap imaps ldap ldaps pop3 pop3s rtsp smb smbs smtp smtps telnet tftp
        Features: AsynchDNS IPv6 Largefile GSS-API Kerberos SPNEGO NTLM NTLM_WB SSL libz UnixSockets

        $ curl --negotiate -u : http://master.example.com:50070  # get a HTTP ticket for master.example.com

   After doing one of these, you should be able to access any of the pages from
   your browser.


.. toctree::
    :maxdepth: 2
    :hidden:

    cli.rst
    travis.rst


.. _Hadoop: http://hadoop.apache.org/
.. _Kerberos: https://web.mit.edu/kerberos/
.. _an online book: https://steveloughran.gitbooks.io/kerberos_and_hadoop/
.. _Lovecraftian Horrors: https://en.wikipedia.org/wiki/H._P._Lovecraft
.. _Docker: https://www.docker.com/
.. _Docker Compose: https://docs.docker.com/compose/
.. _this documentation from Cloudera: https://www.cloudera.com/documentation/enterprise/5-9-x/topics/cdh_sg_browser_access_kerberos_protected_url.html
.. _miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _git: https://git-scm.com/
.. _maven: https://maven.apache.org/
.. _CDH 5: https://www.cloudera.com/documentation/enterprise/5-16-x/topics/cdh_intro.html
.. _CDH 6: https://www.cloudera.com/documentation/enterprise/6/6.2/topics/cdh_intro.html
.. _jcrist/hadoop-testing-cdh5: https://cloud.docker.com/repository/docker/jcrist/hadoop-testing-cdh5
.. _jcrist/hadoop-testing-cdh6: https://cloud.docker.com/repository/docker/jcrist/hadoop-testing-cdh6
