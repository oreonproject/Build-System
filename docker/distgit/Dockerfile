FROM registry.fedoraproject.org/fedora:41
MAINTAINER copr-devel@lists.fedorahosted.org

ARG ADDITIONAL_COPR_REPOSITORIES="@copr/copr-dev"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux
ENV PYTHONPATH=/usr/share/copr/

# base packages
RUN set -ex ; \
    test -z "${ADDITIONAL_COPR_REPOSITORIES}" \
        || dnf -y install dnf-plugins-core \
        && for repo in $ADDITIONAL_COPR_REPOSITORIES ; do dnf -y copr enable $repo; done ; \
    dnf -y update && \
    dnf -y install htop \
                   which \
                   wget \
                   vim \
                   cgit \
                   python3-rpkg \
                   tini \
                   && \
    dnf -y install dist-git && \
    dnf clean all

# Create users and groups needed for the service
RUN groupadd -r packager 2>/dev/null || true && \
    groupadd -r apache 2>/dev/null || true && \
    groupadd -r copr-dist-git && \
    useradd -r -g copr-dist-git -G packager,apache -c 'copr-dist-git user' -d /home/copr-dist-git -s /bin/bash copr-dist-git

RUN rm /etc/httpd/conf.d/ssl.conf

RUN echo "AliasMatch \"/repo(/.*)/md5(/.*)\" \"/var/lib/dist-git/cache/lookaside\\$1\\$2\"" >> /etc/httpd/conf.d/dist-git/lookaside-copr.conf && \
    echo "Alias /repo/ /var/lib/dist-git/cache/lookaside/" >>  /etc/httpd/conf.d/dist-git/lookaside-copr.conf

RUN sed -i 's/Listen 80/Listen 5001/' /etc/httpd/conf/httpd.conf

RUN mkdir /tmp/copr-dist-git
RUN chown copr-dist-git:packager /tmp/copr-dist-git

RUN mkdir /var/lock/copr-dist-git/
RUN chown copr-dist-git:copr-dist-git /var/lock/copr-dist-git/

# copy filesystem setup and setup ownership and permissions
COPY files/ /
RUN chmod 644 /etc/copr/copr-dist-git.conf

RUN mkdir -p /home/copr-dist-git && \
    echo "[user]" > /home/copr-dist-git/.gitconfig && \
    echo "    email = buildsystem@oreonproject.org" >> /home/copr-dist-git/.gitconfig && \
    echo "    name = Copr dist git" >> /home/copr-dist-git/.gitconfig && \
    chown -R copr-dist-git:copr-dist-git /home/copr-dist-git

RUN sed -i "s/^cache-size.*//" /etc/cgitrc
RUN echo 'scan-path=/var/lib/dist-git/git/rpms' | tee -a /etc/cgitrc

RUN directories="/etc/httpd /var/run/httpd /var/log/httpd /var/lib/dist-git /run/lock" ; \
    chown -R copr-dist-git:root $directories && \
    chmod -R g+rwX $directories

USER copr-dist-git

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "-c", "mkdir -p /var/lib/dist-git/cache /var/lib/dist-git/git && exec /usr/bin/copr-run-dispatcher-dist-git imports"]
