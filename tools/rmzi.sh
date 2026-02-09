#! /usr/bin/bash

echo "Removing Zone Identifier files from current directory and subdirectories"
find . -name "*:Zone.Identifier" -type f -delete
echo "Finished"