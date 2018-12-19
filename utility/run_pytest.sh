#!/usr/bin/env bash
(cd app && pytest --cov-report= --cov=.)
