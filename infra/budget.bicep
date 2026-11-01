targetScope = 'subscription'

@description('Budget name.')
param budgetName string = 'k21-healthcare-budget'

@description('Monthly budget in USD.')
param amount int = 20

@description('Email that receives the alerts. Required, no default: never commit an address.')
param contactEmail string

@description('First day of the current month. The budget API needs a first-of-month start date.')
param startDate string = utcNow('yyyy-MM-01T00:00:00Z')

resource budget 'Microsoft.Consumption/budgets@2024-08-01' = {
  name: budgetName
  properties: {
    category: 'Cost'
    amount: amount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: startDate
    }
    notifications: {
      actual75: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 75
        thresholdType: 'Actual'
        contactEmails: [
          contactEmail
        ]
      }
      actual100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Actual'
        contactEmails: [
          contactEmail
        ]
      }
    }
  }
}
