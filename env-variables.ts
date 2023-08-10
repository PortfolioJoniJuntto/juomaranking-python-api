// You can also create stage depending environment variables (eg. external API urls etc..)
const variables: any = {
  environmentVariable1: {
    dev: 'development environment value',
    prod: 'production environment value',
  },
}

// "Static variables", meaning eg. dynamodb table names
// that are nearly same in development and production environments
const baseName = '${self:service}-${self:provider.stage}'

const account_id = '${aws:accountId}'

const generateVariable = (vars: string | string[]) => {
  if (typeof vars === 'string') {
    return `${baseName}-${vars}`
  }

  return `${baseName}-${vars.join('-')}`
}

const staticVars = {
  products_table_name: generateVariable('products'),
  ratings_table_name: generateVariable('ratings'),
  pricehistory_table_name: generateVariable('pricehistory'),
  users_table_name: generateVariable('users'),
  public_content_bucket_name: generateVariable(['public-content', account_id]),
  user_pool_id: {
    'Fn::ImportValue': generateVariable('UserPoolId'),
  },
  user_pool_client_id: {
    'Fn::ImportValue': generateVariable('UserPoolClientId'),
  },
  region: '${self:provider.region}',
}

// Parse variable list from two objects above and return it
// These variables are exposed in the code
export const getEnvVariables = (stage: string) => {
  const vars: any = {}

  Object.keys(variables).forEach((key: string) => {
    vars[key] = variables[key][stage]
  })

  return {
    ...vars,
    ...staticVars,
  }
}
