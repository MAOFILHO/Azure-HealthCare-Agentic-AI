#!/usr/bin/env bash
# Delete the whole resource group. Asks for the group name first.
# Needs `az login`.
set -euo pipefail

group="K21-project-rg"

read -r -p "This deletes resource group $group and everything in it. Type its name to confirm: " answer || true
if [ "${answer:-}" != "$group" ]; then
  echo "Name did not match. Nothing deleted." >&2
  exit 1
fi

az group delete --name "$group" --yes
echo "Deleted $group."
