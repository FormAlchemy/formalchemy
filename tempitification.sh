#!/bin/sh
for i in $(ls *.mako);
do
    echo "$i""_tmpl"
    echo "{{if template_engine == 'mako'}}" > "$i""_tmpl"
    cat $i >> "$i""_tmpl"
    echo "{{endif}}" >> "$i""_tmpl"
    rm "$i"
done
