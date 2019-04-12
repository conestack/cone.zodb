#!/bin/sh
./$1/bin/coverage run --source src/cone/zodb -m cone.zodb.tests.__init__
./$1/bin/coverage report
./$1/bin/coverage html
