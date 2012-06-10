#!/bin/bash

if [ $# -ne 1 ];
then
    echo 'make-dmg.sh [version]'
    exit
fi

source='dist/ostrich.app'
title='ostrich-go'
size=40000
dmg_name='releases/ostrich-go_'$1

python setup.py py2app -S -r gnugo-3.8
mv dist/ostrich.app/Contents/Frameworks/gnugo-3.8 dist/ostrich.app/Contents/Resources/gnugo-3.8
hdiutil create -srcfolder "${source}" -volname "${title}" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${size}k pack.temp.dmg

device=$(hdiutil attach -readwrite -noverify -noautoopen "pack.temp.dmg" | egrep '^/dev/' | sed 1q | awk '{print $1}')

chmod -Rf go-w /Volumes/"${title}"
sync
sync
hdiutil detach ${device}
hdiutil convert "pack.temp.dmg" -format UDZO -imagekey zlib-level=9 -o "${dmg_name}"
rm -f pack.temp.dmg 
