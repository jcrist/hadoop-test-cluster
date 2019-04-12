FROM centos:centos7
MAINTAINER jcrist

# Install common utilities
RUN yum install -y \
        sudo \
        git \
        bzip2 \
        java-1.8.0-openjdk-devel \
    && yum clean all \
    && rm -rf /var/cache/yum

# Install maven
RUN curl -O www.apache.org/dist/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz \
    && tar xzf apache-maven-3.3.9-bin.tar.gz \
    && mkdir /usr/local/maven \
    && mv apache-maven-3.3.9/ /usr/local/maven/ \
    && alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-3.3.9/bin/mvn 1 \
    && rm apache-maven-3.3.9-bin.tar.gz

# Install supervisord
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && pip install supervisor \
    && rm get-pip.py

# Make a non-privileged account for edge node and install conda for that account
RUN useradd -m testuser
USER testuser

RUN curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && /bin/bash /tmp/miniconda.sh -b -p /home/testuser/miniconda \
    && rm /tmp/miniconda.sh \
    && echo 'export PATH="/home/testuser/miniconda/bin:$PATH"' >> /home/testuser/.bashrc \
    && /home/testuser/miniconda/bin/conda update conda -y \
    && /home/testuser/miniconda/bin/conda config --set always_yes yes --set changeps1 no

# Copy over files
COPY --chown=testuser ./testuser /home/testuser

# Revert to root permissions for rest of file
USER root

# Install fixuid
RUN curl -SsL https://github.com/boxboat/fixuid/releases/download/v0.4/fixuid-0.4-linux-amd64.tar.gz | tar -C /usr/local/bin -xzf - \
    && chown root:root /usr/local/bin/fixuid \
    && chmod 4755 /usr/local/bin/fixuid \
    && echo "root ALL=(ALL:ALL) NOPASSWD: /usr/local/bin/fixuid" >> /etc/sudoers

# Copy over files
COPY ./files /

# Create a few more accounts to test proxyuser support
RUN useradd -m alice
RUN useradd -m bob
