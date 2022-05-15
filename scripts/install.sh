#!/bin/bash

./scripts/clean.sh

function install {
    local interpreter=$1
    local target=$2
    local pinned_packages="$3"

    if [ -x "$(which $interpreter)" ]; then
        virtualenv --clear -p $interpreter $target
        ./$target/bin/pip install wheel coverage
        ./$target/bin/pip install $pinned_packages
        ./$target/bin/pip install https://github.com/conestack/node/archive/master.zip
        ./$target/bin/pip install -e .[test]
    else
        echo "Interpreter $interpreter not found. Skip install."
    fi
}

install python2 py2 "pyramid==1.9.4 repoze.zcml==0.4 repoze.workflow==0.6.1"
install python3 py3 "pyramid==1.9.4 repoze.zcml==1.0b1 repoze.workflow==1.0b1"
