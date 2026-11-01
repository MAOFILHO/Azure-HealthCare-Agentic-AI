#!/usr/bin/env bash
# Deploy infra/main.bicep at subscription scope, then write the Foundry
# endpoints to a local, untracked env file. Needs `az login`.
#
#   infra/deploy.sh --what-if   preview the changes; changes nothing
#   infra/deploy.sh             deploy and write the env file
#   infra/deploy.sh --budget-email ADDRESS
#                               also deploy infra/budget.bicep (20 USD a month,
#                               alerts at 75% and 100% of actual cost)
#
# ENV_FILE overrides where the values go (default: .env.foundry at the repo
# root, which .gitignore covers). The values are never printed.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
env_file="${ENV_FILE:-$here/../.env.foundry}"
location="${LOCATION:-eastus2}"
deployment="k21-healthcare"

what_if=0
budget_email=""
usage() { echo "usage: deploy.sh [--what-if] [--budget-email ADDRESS]" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --what-if) what_if=1; shift ;;
    --budget-email) [ $# -ge 2 ] || usage; budget_email="$2"; shift 2 ;;
    *) usage ;;
  esac
done

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

if [ -n "$budget_email" ]; then
  az deployment sub create \
    --name "$deployment-budget" --location "$location" \
    --template-file "$here/budget.bicep" \
    --parameters contactEmail="$budget_email" \
    --output none
fi

umask 077
{
  echo "FOUNDRY_PROJECT_ENDPOINT=$project_endpoint"
  echo "FOUNDRY_MODEL_DEPLOYMENT_NAME=$model_name"
  echo "FOUNDRY_RESOURCE_ENDPOINT=$resource_endpoint"
} > "$env_file"
chmod 600 "$env_file"

echo "Deployed. Wrote 3 variables to the env file (values not shown)."
