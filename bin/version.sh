#!/usr/bin/env bash
get_version_revision() {
    git describe
}

get_closest_version() {
	git describe --abbrev=0
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