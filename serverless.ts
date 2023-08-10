import type { AWS } from '@serverless/typescript'
import { getEnvVariables } from './env-variables'
import { Outputs as PermanentOutputs, Resources as PermanentResources } from './permanent-stack'
import functions from '@functions/index'

const { stage } = require('minimist')(process.argv.slice(2))

if (!stage) {
  throw new Error('Stage is missing!')
}

// Load environment variables from the file based on stage
const environmentVariables = getEnvVariables(stage)

const serverlessConfiguration: AWS = {
  service: 'juomaranking-api',
  frameworkVersion: '3.22.0',
  plugins: ['serverless-python-requirements', 'serverless-offline', 'serverless-plugin-additional-stacks', 'serverless-esbuild'],
  provider: {
    name: 'aws',
    region: 'eu-north-1',
    deploymentMethod: 'direct',
    stage: "${opt:stage, 'dev'}",
    apiGateway: {
      minimumCompressionSize: 1024,
    },
    environment: environmentVariables,
    lambdaHashingVersion: '20201221',
    iam: {
      role: {
        statements: [
          {
            Effect: 'Allow',
            Action: [
              'dynamodb:Query',
              'dynamodb:Scan',
              'dynamodb:GetItem',
              'dynamodb:UpdateItem',
              'dynamodb:DeleteItem',
              'dynamodb:PutItem',
              'dynamodb:DescribeTable',
              'dynamodb:BatchGetItem',
              'dynamodb:BatchPutItem',
              'dynamodb:BatchWriteItem',
            ],
            Resource: [
              {
                'Fn::Sub': 'arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${self:service}-${self:provider.stage}-*',
              },
              {
                'Fn::Sub': 'arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${self:service}-${self:provider.stage}-*/index/*',
              },
            ],
          },
          {
            Effect: 'Allow',
            Action: ['s3:PutObject'],
            Resource: [
              {
                'Fn::Sub': 'arn:aws:s3:::${self:service}-${self:provider.stage}-*',
              },
            ],
          },
          {
            Effect: 'Allow',
            Action: ['cognito-idp:*'],
            Resource: [
              {
                'Fn::Sub': '*',
              },
            ],
          },
        ],
      },
    },
    httpApi: {
      cors: true,
      authorizers: {
        serviceAuthorizer: {
          identitySource: '$request.header.Authorization',
          issuerUrl: {
            'Fn::Join': ['', ['https://cognito-idp.', '${self:provider.region}', '.amazonaws.com/', '${self:provider.environment.user_pool_id}']],
          },

          audience: ['${self:provider.environment.user_pool_client_id}'],
        },
      },
    },
    ecr: {
      images: {
        'juomaranking-api': {
          path: './src/functions/app',
        },
        'image-download-handler': {
          path: './src/functions/image-download-handler',
        },
      },
    },
  },
  custom: {
    additionalStacks: {
      permanent: {
        Deploy: 'Before',
        Resources: PermanentResources,
        Outputs: PermanentOutputs,
      },
    },
    esbuild: {
      bundle: true,
      minify: true,
      sourcemap: true,
      exclude: ['aws-sdk'],
      target: 'node16',
      define: { 'require.resolve': undefined },
      platform: 'node',
    },
  },
  package: {
    individually: true,
  },
  functions: {
    api: {
      image: 'juomaranking-api',
      environment: {
        STAGE: '${self:provider.stage}',
      },
      timeout: 30,
      events: [
        {
          httpApi: {
            method: 'any',
            path: '/{proxy+}',
          },
        },
      ],
    },
    ...functions,
  },
}

module.exports = serverlessConfiguration
