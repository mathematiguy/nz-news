#!/bin/bash

# Log commands as they run and fail noisily
set -ex

# Set environment variables
export RUN=

# Run crawler
make crawl

# Send articles to /output
cp data/nzherald.json /output
