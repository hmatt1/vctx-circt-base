# python-3.14t-with-circt

This repo builds a base docker image with free-threaded Python (`3.14t`) with GIL disabled and CIRCT python bindings.

Build CIRCT from source only once when creating the base image; do not repeatedly compile CIRCT in normal local/CI workflows.

