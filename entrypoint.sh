#!/bin/bash

python3 models.py
python3 server.py

exec "$@"