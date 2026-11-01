targetScope = 'subscription'

@description('Resource group that holds the Foundry resource and project.')
param resourceGroupName string = 'K21-project-rg'

@description('Foundry resource (AIServices account) name. Also the custom subdomain.')
param foundryName string = 'k21-healthcare'

@description('Foundry project name.')
param projectName string = 'K21-healthcare'

@description('Azure region.')
param location string = 'eastus2'

@description('Object id of the user or service principal that runs the labs (az ad signed-in-user show --query id).')
param principalId string

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

module foundry 'foundry.bicep' = {
  name: 'foundry'
  scope: rg
  params: {
    foundryName: foundryName
    projectName: projectName
    location: location
  }
}

module roles 'roles.bicep' = {
  name: 'roles'
  scope: rg
  params: {
    foundryName: foundryName
    principalId: principalId
  }
  dependsOn: [
    foundry
  ]
}

module models 'models.bicep' = {
  name: 'models'
  scope: rg
  params: {
    foundryName: foundryName
  }
  dependsOn: [foundry]
}

output projectEndpoint string = foundry.outputs.projectEndpoint
output resourceEndpoint string = foundry.outputs.resourceEndpoint
output chatDeploymentName string = models.outputs.chatDeploymentName
output embeddingDeploymentName string = models.outputs.embeddingDeploymentName
