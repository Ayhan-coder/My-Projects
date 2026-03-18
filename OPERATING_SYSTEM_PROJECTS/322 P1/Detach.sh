#!/bin/bash

sudo rmmod machine 2>/dev/null || true
sudo rm -f /dev/cmachine
echo "Module detached."
