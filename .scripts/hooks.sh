#!/bin/bash
# author: dzamora, apoquet
# version: 1.0
# '######################################################'
# '#               Git hooks installation               #'
# '######################################################'

hooks_dir='.git/hooks/'
lint_command='pipenv run linter'
test_command='pipenv run test'

list_result=$(find $hooks_dir* -maxdepth 1 ! -name '*.sample')

if [[ -z "$list_result" ]]; then
  precommit="#!/usr/bin/env bash\n$lint_command"
  prepush="#!/usr/bin/env bash\n$lint_command\n$test_command"
  pre_commit_bin="$hooks_dir/pre-commit"
  pre_push_bin="$hooks_dir/pre-push"
  echo -e "$precommit" >"$pre_commit_bin"
  echo -e "$prepush" >"$pre_push_bin"
  chmod +x "$pre_commit_bin"
  chmod +x "$pre_push_bin"
  echo 'Git hooks installed successfully'
else
  rm "$hooks_dir/pre-commit"
  rm "$hooks_dir/pre-push"
  echo 'Git hooks uninstalled successfully'
fi
