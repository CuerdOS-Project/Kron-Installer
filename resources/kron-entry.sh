#!/bin/bash

if [ "$USER" = "anon" ]; then
    cp /usr/share/applications/kron.desktop ~/Desktop/kron.desktop
    chmod +x ~/Desktop/kron.desktop
	gio set ~/Desktop/kron.desktop -t string metadata::trust "true"
fi
