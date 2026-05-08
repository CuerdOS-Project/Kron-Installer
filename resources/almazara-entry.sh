#!/bin/bash

if [ "$USER" = "anon" ]; then
    cp /usr/share/applications/almazara.desktop ~/Desktop/almazara.desktop
    chmod +x ~/Desktop/almazara.desktop
	gio set ~/Desktop/almazara.desktop -t string metadata::trust "true"
fi
