#!/usr/bin/env bash

## Install Basic Detokenizer from https://github.com/gfis/basdetok/
## https://github.com/gfis/basdetok/blob/master/src/main/java/org/teherba/basdetok/M20Detokenizer.java

cond_apt() {
    # conditional apt 
    dpkg -s $1 >/dev/null || sudo apt install $1
}

cond_apt ant
cond_apt tomcat9

if ! [ -d "/usr/share/tomcat" ]; then
    (cd /usr/share/; sudo ln -s tomcat9 tomcat)
fi

# get apache log4j
wget https://dlcdn.apache.org/logging/log4j/2.19.0/apache-log4j-2.19.0-bin.zip
unzip apache-log4j-2.19.0-bin.zip
rm apache-log4j-2.19.0-bin.zip
sleep 1

# get apache commons fileupload
wget https://dlcdn.apache.org//commons/fileupload/binaries/commons-fileupload-1.4-bin.zip
unzip commons-fileupload-1.4-bin.zip
rm commons-fileupload-1.4-bin.zip
sleep 1

# get gfis common
wget https://github.com/gfis/common/archive/refs/heads/master.zip
unzip master.zip
rm master.zip
mv common-master common
(cd common; mkdir -p dist lib expand)
cp apache-log4j-2.19.0-bin/log4j-api-2.19.0.jar common/lib/
cp apache-log4j-2.19.0-bin/log4j-core-2.19.0.jar common/lib/
cp commons-fileupload-1.4-bin/commons-fileupload-1.4.jar common/lib/
(cd common; ant dist)
sleep 1

# get basdetok master
wget https://github.com/gfis/basdetok/archive/refs/heads/master.zip
unzip master.zip
rm master.zip
sleep 1
#mv basdetok-master basdetok
(cd basdetok-master; mkdir -p dist lib expand)
cp apache-log4j-2.19.0-bin/log4j-api-2.19.0.jar basdetok-master/lib/
cp apache-log4j-2.19.0-bin/log4j-core-2.19.0.jar basdetok-master/lib/
cp commons-fileupload-1.4-bin/commons-fileupload-1.4.jar basdetok-master/lib/
cp common/dist/common-core.jar basdetok-master/lib/
(cd basdetok-master; ant dist; ant)
sleep 1

cp basdetok-master/dist/basdetok.jar .
zip -r basdetok.zip basdetok-master
rm -rf apache-log4j-2.19.0-bin common commons-fileupload-1.4-bin basdetok-master
echo

java -jar basdetok.jar
