#!/bin/sh
# shellcheck shell=sh
# -------------------------------------------------------------------------------------
# Summary: Install system dependencies to `alpine` images.
# Created: 2021-11-10 20:28:59
# Author:  Bryant Finney <finneybp@gmail.com> (https://bryant-finney.github.io/about)
#
# Usage:
#   To install the minimal system dependencies:
#       ./install_alpine_deps.sh
#
#   For extra development dependencies:
#       ./install_alpine_deps.sh --extras
# -------------------------------------------------------------------------------------

parse_args() {
	# Parse the arguments, setting environment variables.
	#
	#   See also: function show_help()
	#
	#   Args:
	#       $@                      the arguments to parse
	#
	#   Returns:
	#       $DEV

	while test $# -gt 0; do
		case "$1" in
		-e | --extras)
			export INSTALL_EXTRAS=true
			shift 1
			;;

		*)
			error "Unrecognized argument: $1"
			exit 1
			;;
		esac
	done
}

parse_args "$@"

apk add git gcc build-base linux-headers libxslt-dev libffi-dev openssl-dev \
	musl-dev cargo rust postgresql-dev postgresql-client ttf-freefont

# this package is required for `pyreverse`, `pydeps`, and other `dev` dependencies
if [ "$INSTALL_EXTRAS" = "true" ]; then
	apk add graphviz-dev zsh neovim jq gnupg git neovim curl
fi
