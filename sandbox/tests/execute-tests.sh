#! /bin/bash

setUp()
{
    [ -d "output" ] && { rm -rf output ; mkdir output ; } || mkdir output 
}

tearDown()
{
    rm -rf output
}

oneTimeSetUp() {
    git clone https://github.com/checkmarx-ltd/cx-flow.git cxflow
}

oneTimeTearDown() {
    [ -d "cxflow" ] && rm -rf cxflow || :
}
