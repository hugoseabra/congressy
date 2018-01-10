#!/usr/bin/env bash
get_version_revision() {
    local VERSION=''
	local TAGS=$(git tag -l)

	if [[ ! $TAGS ]]; then
	    VERSION=$(git rev-parse HEAD)
    else
        VERSION=$(git describe)
	fi

	echo $VERSION
}

get_closest_version() {
	local CLOSEST_TAG=$(git describe --abbrev=0)
	local VERSION=$(echo $CLOSEST_TAG | python -c "import sys; print(sys.stdin.read().partition('v')[-1])")
	echo $VERSION
}

git_next_major_version(){
	local CLOSEST_VERSION=$(get_closest_version)
	local NEW_TAG=$( echo $CLOSEST_VERSION | python -c 'import semver, sys; print(semver.bump_major(sys.stdin.read()))')
	echo $NEW_TAG
}

git_next_minor_version(){
	local CLOSEST_VERSION=$(get_closest_version)
	local NEW_TAG=$( echo $CLOSEST_VERSION | python -c 'import semver, sys; print(semver.bump_minor(sys.stdin.read()))')
	echo $NEW_TAG
}

git_next_patch_version(){
    local CLOSEST_VERSION=$(get_closest_version)
    local NEW_TAG=$( echo $CLOSEST_VERSION | python -c 'import semver, sys; print(semver.bump_patch(sys.stdin.read()))')
    echo $NEW_TAG
}

case $1 in
	"patch") git_next_patch_version ;;
	"minor") git_next_minor_version ;;
	"major") git_next_major_version ;;
	"version") get_closest_version ;;
	"full_version") get_version_revision ;;
	*) get_closest_version ;;
esac