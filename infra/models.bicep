param foundryName string

@description('Chat model. Change with the capacity if the subscription has no quota for the default.')
param chatModel string = 'gpt-5-mini'

@description('Chat model version. Empty uses the default version for the model.')
param chatModelVersion string = ''

@description('Chat capacity in thousands of tokens per minute.')
param chatCapacity int = 50

@description('Embedding model.')
param embeddingModel string = 'text-embedding-3-large'

@description('Embedding model version. Empty uses the default version for the model.')
param embeddingModelVersion string = ''

@description('Embedding capacity in thousands of tokens per minute.')
param embeddingCapacity int = 50

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: foundryName
}

resource chat 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: foundry
  name: chatModel
  sku: {
    name: 'GlobalStandard'
    capacity: chatCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: chatModel
      version: empty(chatModelVersion) ? null : chatModelVersion
    }
  }
}

// Deployments on one account are created one at a time; a parallel PUT can fail with RequestConflict.
resource embedding 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: foundry
  name: embeddingModel
  dependsOn: [chat]
  sku: {
    name: 'GlobalStandard'
    capacity: embeddingCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModel
      version: empty(embeddingModelVersion) ? null : embeddingModelVersion
    }
  }
}

output chatDeploymentName string = chat.name
output embeddingDeploymentName string = embedding.name
