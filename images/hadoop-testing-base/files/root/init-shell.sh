#!/bin/bash

# Wait for fixuid to have finished
while [[ ! -f /var/run/fixuid.ran ]]
do
    sleep 1
done

# cd into home directory
cd

# initialize as if login shell
if [ -f .bash_profile ]; then
    source .bash_profile;
fi
