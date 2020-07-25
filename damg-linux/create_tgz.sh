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

BIN_NAME="eCloudCLI.DAMG.Linux.stable01"
echo -n -e "\r[                                                                        0% ]"
sleep 0.1

# Clear expire files or directories.
rm -f ./$BIN_NAME.bin >/dev/null 2>&1
rm -f ./$BIN_NAME.tgz >/dev/null 2>&1
rm -rf dist build __pycache__ *.spec target.tgz >/dev/null 2>&1
echo -n -e "\r[ =======                                                               10% ]"
sleep 1

# Make the executable files.
/opt/python3/bin/pyinstaller -F dam_collect.py >/dev/null 2>&1
echo -n -e "\r[ ========================                                              30% ]"

/opt/python3/bin/pyinstaller -F dam_high_frequency.py >/dev/null 2>&1
echo -n -e "\r[ ============================================                          60% ]"

# Make the executable files.
/opt/python3/bin/pyinstaller -F dam_daemon.py >/dev/null 2>&1
echo -n -e "\r[ ================================================================      90% ]"

# Make the configuration.
echo '[public]' > ./dist/damg.conf
echo 'start_time =' >> ./dist/damg.conf
echo 'cycle_time =' >> ./dist/damg.conf
echo 'if_wmconcat = yes' >> ./dist/damg.conf
echo 'limit_cpu = 80' >> ./dist/damg.conf
echo 'limit_iops = 50000' >> ./dist/damg.conf
echo 'listen_host =' >> ./dist/damg.conf
echo '' >> ./dist/damg.conf
echo '[oracle]' >> ./dist/damg.conf
echo 'health_time = 7' >> ./dist/damg.conf
echo 'sys_password =' >> ./dist/damg.conf
echo 'users =' >> ./dist/damg.conf
sleep 0.1

# Move the sql file.
cp create_wmconcat.sh ./dist/

#
# Compress it.
#
tar cvzf target.tgz dist >/dev/null 2>&1

#
# Build a new bin file.
#
cat install.sh target.tgz >$BIN_NAME.bin
chmod +x ./$BIN_NAME.bin >/dev/null 2>&1

tar cvzf $BIN_NAME.tgz $BIN_NAME.bin >/dev/null 2>&1
rm -f $BIN_NAME.bin >/dev/null 2>&1

# Clear expire files or directories.
rm -rf dist build __pycache__ *.spec target.tgz >/dev/null 2>&1
echo -n -e "\r[ =============================================================== Comp1ete! ]"
sleep 1

echo -e "\n<"$BIN_NAME"> created."
exit 0
