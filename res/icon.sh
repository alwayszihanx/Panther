#!/bin/sh

# Rasterize the main app logo (res/logo.svg) into a Chromium icon PNG.
tpl=$(dirname "$0")/logo.svg
w=$(identify -format %w "$1")
rsvg-convert -w "$w" -h "$w" "$tpl" -o "$1"
echo "$1 (${w}px, logo)"
