#!/bin/bash  

sudo dnf -y install gnupg2 pcsc-lite-ccid
sudo systemctl enable pcscd

tee ~/.gnupg/gpg-agent.conf << EOF
default-cache-ttl 86400
max-cache-ttl 999999
enable-ssh-support
EOF

tee ~/.gnupg/scdaemon.conf << EOF
card-timeout 1800
EOF

sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/dirmngr.service /etc/systemd/user/dirmngr.service
sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/dirmngr.socket /etc/systemd/user/dirmngr.socket
sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/gpg-agent-browser.socket /etc/systemd/user/gpg-agent-browser.socket
sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/gpg-agent-extra.socket /etc/systemd/user/gpg-agent-extra.socket
sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/gpg-agent-ssh.socket /etc/systemd/user/gpg-agent-ssh.socket
sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/gpg-agent.service /etc/systemd/user/gpg-agent.service
sudo ln -s /usr/share/doc/gnupg2/examples/systemd-user/gpg-agent.socket /etc/systemd/user/gpg-agent.socket

sudo systemctl daemon-reload

systemctl --user enable dirmngr.socket
systemctl --user enable gpg-agent-browser.socket
systemctl --user enable gpg-agent-extra.socket
systemctl --user enable gpg-agent-ssh.socket
systemctl --user enable gpg-agent.socket

tee -a ~/.bashrc << EOF
export SSH_AUTH_SOCK="/run/user/\$(id -u)/gnupg/S.gpg-agent.ssh"
EOF
