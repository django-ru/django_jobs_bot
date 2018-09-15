#!/usr/bin/env bash

SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="django-jobs-bot.service"

cp ${SERVICE_NAME} "${SYSTEMD_DIR}/${SERVICE_NAME}"
chmod 664 "${SYSTEMD_DIR}/${SERVICE_NAME}"
systemctl daemon-reload
systemctl start ${SERVICE_NAME}
systemctl status ${SERVICE_NAME}
