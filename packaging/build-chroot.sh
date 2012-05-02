#!/usr/bin/env bash
###############################################################################
# nanoengineer-chroot creator
#
# This installs Ubuntu 7.04 into a chroot. You should probably just use the 
# archive of the created chroot rather than re-creating it from scratch.
#
# created: 2012-04-29
# updated: 2012-04-30
#
# blame:
#   Bryan Bishop <kanzure@gmail.com>
#   Joe Rayhawk <jrayhawk@omgwallhack.org>
#
# support:
#   irc.freenode.net ##hplusroadmap
#
# links:
#   http://diyhpl.us/~bryan/irc/nanoengineer/nanoengineer-chroot.tar.gz (1.2 GB)
#   http://github.com/kanzure/nanoengineer
#   http://groups.google.com/group/nanoengineer-dev
#   http://nanoengineer-1.net/
#   http://nanorex.com/
#
# backup mirror of some packages:
#   http://diyhpl.us/~bryan/irc/nanoengineer/dependencies/
#
# An error like:
#   mknod: `$CHROOT/test-dev-null`: Operation not permitted
#   E: Cannot install into target '$CHROOT' mounted with noexec or nodev
# on a vserver means that debootstrap is looking to install device nodes, so
# you will have to create this outside the vserver environment.
#
# Note: you can't actually run this file, but it should be easy to follow along.
###############################################################################

export CHROOT=/root/nanoengineer-chroot
mkdir -p $CHROOT

# install a known working version of ubuntu
sudo apt-get install debootstrap
sudo debootstrap --arch i386 feisty $CHROOT http://old-releases.ubuntu.com/ubuntu/

# switch into the chroot
sudo chroot $CHROOT

# this should be refactored
exit

# this is for git config later
export GHUSERNAME="your github username"
export FULLNAME="Jack Saturn"
export EMAIL="jack@saturn.com"

# add a user to the chroot
# username: nanoengineeruser
# password: password
adduser nanoengineeruser

# add the user to sudoers
visudo

# switch to the user
su nanoengineeruser

# add "universe"
sudo vim /etc/apt/sources.list
sudo apt-get update

# set 'readline' and 'low'
dpkg-reconfigure debconf

# necessary to get locales working?
export LANG=C

sudo apt-get install locales git-core python2.5-dev g++ libqt4-dev \
     qt4-dev-tools qt4-qtconfig python-numarray=1.5.2-2.2ubuntu1 \
     python-numeric-ext=24.2-7ubuntu1 libgle3 python-imaging=1.1.6-0ubuntu3 \
     libdb4.5=4.5.20-1ubuntu1 libdb4.5-dev=4.5.20-1ubuntu1 wget make \
     python-setuptools automake libtool unzip libhdf5-serial-dev python-pyrex \
     freeglut3 mesa-utils libgl1-mesa-swx11

mkdir -p ~/locals
cd ~/locals

# download and install pybsddb
mkdir -p ~/local/pybsddb; cd ~/local/pybsddb
wget http://www.nanoengineer-1.com/bhelfrich/BuildMeister/bsddb3-4.5.0.tar.gz
tar -zxvf bsddb3-4.5.0.tar.gz
sudo python setup.py install

# download and install sip 4.7.4
mkdir ~/local/sip; cd ~/local/sip
wget http://www.nanoengineer-1.com/bhelfrich/BuildMeister/sip-4.7.4.tar.gz
tar -zxvf sip-4.7.4.tar.gz
cd sip-4.7.4
python configure.py
make
sudo make install

# download and install pyqt 4.3.3
mkdir ~/local/pyqt; cd ~/local/pyqt
wget http://www.nanoengineer-1.com/bhelfrich/BuildMeister/PyQt-x11-gpl-4.3.3.tar.gz
tar -zxvf PyQt-x11-gpl-4.3.3.tar.gz
cd PyQt-x11-gpl-4.3.3/
# you will need to type "YES"
python configure.py
# this next one will take a while.. why isn't there a package for 4.3.3?
time make
sudo make install

# repos only have numpy 1.0.1
mkdir ~/local/numpy; cd ~/local/numpy
wget http://www.nanoengineer-1.com/bhelfrich/BuildMeister/numpy-1.0.2.tar.gz
tar -zxvf numpy-1.0.2.tar.gz
cd numpy-1.0.2/
sudo python setup.py install

# ctypes
mkdir ~/local/ctypes; cd ~/local/ctypes
wget http://www.nanoengineer-1.com/bhelfrich/BuildMeister/ctypes-1.0.2.tar.gz
tar -zxvf ctypes-1.0.2.tar.gz
cd ctypes-1.0.2/
sudo python setup.py install

# pyopengl
mkdir ~/local/pyopengl; cd ~/local/pyopengl
wget http://www.nanoengineer-1.com/bhelfrich/BuildMeister/PyOpenGL-3.0.0a6.tar.gz
tar -zxvf PyOpenGL-3.0.0a6.tar.gz
cd PyOpenGL-3.0.0a6/
sudo python setup.py install

# pyrex
mkdir -p ~/local/pyrex; cd ~/local/pyrex
wget "http://pkgs.fedoraproject.org/repo/pkgs/Pyrex/Pyrex-0.9.3.1.tar.gz/0415b95a023061679021323d9ce56fe0/Pyrex-0.9.3.1.tar.gz"
tar -zxvf Pyrex-0.9.3.1.tar.gz
cd Pyrex-0.9.3.1/
sudo python setup.py install

# get the nanoengineer sources
mkdir -p ~/code
cd ~/code
git clone git://diyhpl.us/nanoengineer.git nanoengineer 
cd ~/code/nanoengineer

# get a particular version of the sources
#git checkout 4a5b6dc163d3c248f688433d40d39ae1307d95cf

# any change you make should be on your own branch
git checkout -b experimental

# also.. set up your remotes and config
git config --user.name $FULLNAME
git config --user.email $EMAIL
git remote rm origin
git remote add origin https://$GHUSERNAME@github.com/$GHUSERNAME/nanoengineer.git experimental

# start to compile nanoengineer
./bootstrap
./configure
## Numeric version 24.2 was found. That version may work, but the
## officially supported version is 23.8.

# quick detour
cd ~/code/nanoengineer/sim/src
make version.h
make

# ok now make everything
cd ~/code/nanoengineer
make

# run
DISPLAY=127.0.0.1:11 python ~/code/nanoengineer/cad/src/main.py
