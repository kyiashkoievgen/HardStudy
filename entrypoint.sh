#!/bin/bash

# Установка SSH-туннеля
ssh -o StrictHostKeyChecking=no -f -N -L *:3306:localhost:3306 -i /config/keys/server_key ewgen@bestmail.online &

# Запуск основного приложения
exec "$@"
