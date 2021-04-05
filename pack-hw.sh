#!/bin/bash

echo "packing $1"
zip -r "$1.zip" "$1"
