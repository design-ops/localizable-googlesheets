#!/usr/bin/env bash

echo "Checking localisation checksum"

languages_list=`cat ./.checksum.localizablegooglesheets | cut -d' ' -f2`

if [ -z "$languages_list" ]; then
    echo "Failed to parse the .checksum.localizablegooglesheets file. Is its path correct?"
    exit -1
fi

for language in $languages_list
do
    checksum=`cat ./.checksum.localizablegooglesheets | grep $language | cut -d' ' -f1`

    file=`find . | grep "$language.lproj/Localizable.strings$" | grep -v -e ".app" -e ".build" -e ".framework"`
    file_checksum=`shasum "$file" | cut -d' ' -f1`

    if [ "$checksum" != "$file_checksum" ]; then
        echo "Remember the \"THIS FILE IS GENERATED, DO NOT EDIT IT!\" bit in the $language Localizable.strings file? Well, it was edited!"
        exit -1
    fi
done

echo "Localisations are good!"
exit 0