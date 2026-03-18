#!/bin/bash

# Remove old module if exists
sudo rmmod machine 2>/dev/null || true
sudo rm -f /dev/cmachine

# Insert module with CORRECT parameters
# char_key: 2+0+2+1+4+0+0+2+1+9 = 21
# short_key: 2021400219 % 32767 = 3989 (NOT 439686)
sudo insmod machine.ko char_key=21 short_key=3989 user_string_key="2021400219"

# Create character device file
sudo mknod /dev/cmachine c 444 4

# Set permissions: rw- for all users (no execute)
sudo chmod 666 /dev/cmachine