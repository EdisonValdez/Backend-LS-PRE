#!/bin/bash
# author: dzamora, apoquet
# version: 1.0
# '######################################################'
# '#                Coverage run command                #'
# '######################################################'

coverage run ./manage.py test local_secrets --settings=config.settings.test --noinput
coverage html
coverage report
