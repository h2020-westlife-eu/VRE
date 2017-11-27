#!/usr/bin/env bash

set -eux

export DEBIAN_FRONTEND=noninteractive

apt-get update -y -qq
apt-get install -y -qq build-essential python-dev postgresql-9.4 xmlsec1

apt-get clean
