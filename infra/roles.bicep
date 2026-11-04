// Role assignments for the principal that deploys and runs the labs.
// Scope: the Foundry resource only, so nothing wider than the labs need.
//
// Roles (ids verified with `az role definition list`):
//   Azure AI User (now shown as "Foundry User")  53ca6127-db72-4b80-b1b0-d745d6d5456d
//     lab01 to lab07: create agents, run chats, call tools, use the knowledge base and MCP.
//   Cognitive Services User                      a97b65f3-24c7-4388-baec-2e87135dc908
//     lab05: Content Understanding extraction on the Foundry (AIServices) resource.
param foundryName string

@description('Object id of the signed-in user or service principal that runs the labs.')
param principalId string

@allowed([
  'User'
  'ServicePrincipal'
])
param principalType string = 'User'

var azureAiUser = '53ca6127-db72-4b80-b1b0-d745d6d5456d'
var cognitiveServicesUser = 'a97b65f3-24c7-4388-baec-2e87135dc908'

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: foundryName
}

resource azureAiUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, principalId, azureAiUser)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', azureAiUser)
    principalId: principalId
    principalType: principalType
  }
}

resource cognitiveServicesUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, principalId, cognitiveServicesUser)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUser)
    principalId: principalId
    principalType: principalType
  }
}
