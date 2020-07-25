#!/bin/bash
#
# Copyright (c) 2015-2017 eCloudtech Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of
#   conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list
#   of conditions and the following disclaimer in the documentation and/or other
#   materials provided with the distribution.
# - Neither name of eCloudtech Corporation nor the names of its contributors may be used
#   to endorse or promote products derived from this software without specific prior
#   written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL ECLOUDTECH OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


echo -e "\nEssential Information"
echo "--------------------------------------------------------------------------------"
echo -e "Software:\tDAMG CLI"
echo -e "Version: \tv1.0"
echo -e "Company: \teCloud Technology"
echo -e "\n"


#
# Show the software installation process.
#
echo "Installation Process"
sed -n -e '1,/^exit 0$/!p' $0 >/tmp/target.tgz 2>/dev/null

install_pack="cd /tmp"
$install_pack >/dev/null 2>&1

install_pack="tar xvzf target.tgz"
$install_pack >/dev/null 2>&1

if [ ! -f '/etc/damg.conf' ]; then
    install_pack="mv -f dist/damg.conf /etc/"
    $install_pack >/dev/null 2>&1

    install_pack="chmod 644 /etc/damg.conf"
    $install_pack >/dev/null 2>&1
fi

if_wmconcat=`cat /etc/damg.conf |grep -w if_wmconcat |cut -d'=' -f2`
if [ "$if_wmconcat" == "yes" ]; then
    su - oracle -c 'cat /tmp/dist/create_wmconcat.sh >> ~/create_wmconcat.sh'
    su - oracle -c 'chmod 777 ~/create_wmconcat.sh'
    su - oracle -c '~/create_wmconcat.sh' >/dev/null 2>&1
fi

install_pack="mv -f dist/dam_* /usr/local/bin/"
$install_pack >/dev/null 2>&1

install_pack="chmod 755 /usr/local/bin/dam_*"
$install_pack >/dev/null 2>&1

# Now we only support el6&7
if [ ! -f "/usr/bin/zip" ]; then
    os_version=`rpm -E %rhel`

    if [ "$os_version" == "6" ]; then
        install_pack="mv -f dist/zip.el6 /usr/bin/zip"
    elif [ "$os_version" == "7" ]; then
        install_pack="mv -f dist/zip.el7 /usr/bin/zip"
    fi
    $install_pack >/dev/null 2>&1

    install_pack="chmod 755 /usr/bin/zip"
    $install_pack >/dev/null 2>&1
fi

install_pack="rm -rf dist target.tgz"
$install_pack >/dev/null 2>&1

echo -n -e "\r[ ================================================================== Comp1ete! ]"
echo -e "\nHave a good time!\n"

exit 0
