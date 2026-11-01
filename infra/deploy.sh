#!/usr/bin/env bash
# Deploy infra/main.bicep at subscription scope, then write the Foundry
# endpoints to a local, untracked env file. Needs `az login`.
#
#   infra/deploy.sh --what-if   preview the changes; changes nothing
#   infra/deploy.sh             deploy and write the env file
#
# ENV_FILE overrides where the values go (default: .env.foundry at the repo
# root, which .gitignore covers). The values are never printed.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
env_file="${ENV_FILE:-$here/../.env.foundry}"
location="${LOCATION:-eastus2}"
deployment="k21-healthcare"

what_if=0
case "${1:-}" in
  "") ;;
  --what-if) what_if=1 ;;
  *) echo "usage: deploy.sh [--what-if]" >&2; exit 2 ;;
esac

principal_id="${PRINCIPAL_ID:-$(az ad signed-in-user show --query id --output tsv)}"

if [ "$what_if" -eq 1 ]; then
  exec az deployment sub what-if \
    --name "$deployment" --location "$location" \
    --template-file "$here/main.bicep" \
    --parameters principalId="$principal_id"
fi

outputs="$(az deployment sub create \
  --name "$deployment" --location "$location" \
  --template-file "$here/main.bicep" \
  --parameters principalId="$principal_id" \
  --query "properties.outputs.[projectEndpoint.value, chatDeploymentName.value, resourceEndpoint.value]" \
  --output tsv)"

{
  read -r project_endpoint
  read -r model_name
  read -r resource_endpoint
} <<< "$outputs"

umask 077
{
  echo "FOUNDRY_PROJECT_ENDPOINT=$project_endpoint"
  echo "FOUNDRY_MODEL_DEPLOYMENT_NAME=$model_name"
  echo "FOUNDRY_RESOURCE_ENDPOINT=$resource_endpoint"
} > "$env_file"
chmod 600 "$env_file"

echo "Deployed. Wrote 3 variables to the env file (values not shown)."
