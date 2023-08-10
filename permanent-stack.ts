export const Resources = {
  ProductsTable: {
    Type: 'AWS::DynamoDB::Table',
    Properties: {
      TableName: '${self:provider.environment.products_table_name}',
      BillingMode: 'PAY_PER_REQUEST',
      AttributeDefinitions: [
        {
          AttributeName: 'ean',
          AttributeType: 'S',
        },
      ],
      KeySchema: [
        {
          AttributeName: 'ean',
          KeyType: 'HASH',
        },
      ],
      StreamSpecification: {
        StreamViewType: 'NEW_IMAGE',
      },
    },
  },
  RatingsTable: {
    Type: 'AWS::DynamoDB::Table',
    Properties: {
      TableName: '${self:provider.environment.ratings_table_name}',
      ProvisionedThroughput: {
        ReadCapacityUnits: 1,
        WriteCapacityUnits: 1,
      },
      AttributeDefinitions: [
        {
          AttributeName: 'ean',
          AttributeType: 'S',
        },
        {
          AttributeName: 'userId',
          AttributeType: 'S',
        },
      ],
      KeySchema: [
        {
          AttributeName: 'ean',
          KeyType: 'HASH',
        },
        {
          AttributeName: 'userId',
          KeyType: 'RANGE',
        },
      ],
    },
  },
  PricehistoryTable: {
    Type: 'AWS::DynamoDB::Table',
    Properties: {
      TableName: '${self:provider.environment.pricehistory_table_name}',
      BillingMode: 'PAY_PER_REQUEST',
      AttributeDefinitions: [
        {
          AttributeName: 'ean',
          AttributeType: 'S',
        },
        {
          AttributeName: 'sk',
          AttributeType: 'S',
        },
      ],
      KeySchema: [
        {
          AttributeName: 'ean',
          KeyType: 'HASH',
        },
        {
          AttributeName: 'sk',
          KeyType: 'RANGE',
        },
      ],
    },
  },
  UsersTable: {
    Type: 'AWS::DynamoDB::Table',
    Properties: {
      TableName: '${self:provider.environment.users_table_name}',
      BillingMode: 'PAY_PER_REQUEST',
      AttributeDefinitions: [
        {
          AttributeName: 'userId',
          AttributeType: 'S',
        },
      ],
      KeySchema: [
        {
          AttributeName: 'userId',
          KeyType: 'HASH',
        },
      ],
    },
  },
  CognitoUserPool: {
    Type: 'AWS::Cognito::UserPool',
    Properties: {
      UserPoolName: '${self:service}-${self:provider.stage}',
      UsernameConfiguration: {
        CaseSensitive: false,
      },
      Schema: [
        {
          Name: 'email',
          Required: true,
          Mutable: true,
        },
      ],
      Policies: {
        PasswordPolicy: {
          MinimumLength: 6,
          RequireLowercase: false,
          RequireUppercase: false,
          RequireNumbers: false,
          RequireSymbols: false,
        },
      },
      AutoVerifiedAttributes: ['email'],
      MfaConfiguration: 'OFF',
    },
  },
  AdminUserGroup: {
    Type: 'AWS::Cognito::UserPoolGroup',
    Properties: {
      Description: 'Group for app administrators',
      GroupName: 'Admin',
      UserPoolId: {
        Ref: 'CognitoUserPool',
      },
    },
  },
  ModeratorsUserGroup: {
    Type: 'AWS::Cognito::UserPoolGroup',
    Properties: {
      Description: 'Group for app moderators',
      GroupName: 'Moderator',
      UserPoolId: {
        Ref: 'CognitoUserPool',
      },
    },
  },
  UserPoolClient: {
    Type: 'AWS::Cognito::UserPoolClient',
    Properties: {
      ClientName: '${self:service}-${self:provider.stage}-mobile',
      UserPoolId: {
        Ref: 'CognitoUserPool',
      },
      ExplicitAuthFlows: ['ALLOW_ADMIN_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH'],
    },
  },
  PublicContentBucket: {
    Type: 'AWS::S3::Bucket',
    Properties: {
      BucketName: '${self:provider.environment.public_content_bucket_name}',
      AccessControl: 'PublicRead',
      OwnershipControls: {
        Rules: [
          {
            ObjectOwnership: 'BucketOwnerPreferred',
          },
        ],
      },
    },
  },
  PublicContentBucketPolicy: {
    Type: 'AWS::S3::BucketPolicy',
    Properties: {
      Bucket: {
        Ref: 'PublicContentBucket',
      },
      PolicyDocument: {
        Version: '2012-10-17',
        Statement: [
          {
            Sid: 'AddPerm',
            Effect: 'Allow',
            Principal: '*',
            Action: ['s3:GetObject'],
            Resource: ['arn:aws:s3:::${self:provider.environment.public_content_bucket_name}/*'],
          },
        ],
      },
    },
  },
  DistributionCachePolicy: {
    Type: 'AWS::CloudFront::CachePolicy',
    Properties: {
      CachePolicyConfig: {
        Name: '${self:service}-${self:provider.stage}-cache-policy',
        DefaultTTL: 15778463, // 6 months
        MinTTL: 15778463, // 6 months
        MaxTTL: 31536000, // 1 year
        ParametersInCacheKeyAndForwardedToOrigin: {
          CookiesConfig: {
            CookieBehavior: 'none',
          },
          EnableAcceptEncodingBrotli: 'true',
          EnableAcceptEncodingGzip: 'true',
          HeadersConfig: {
            HeaderBehavior: 'none',
          },
          QueryStringsConfig: {
            QueryStringBehavior: 'none',
          },
        },
      },
    },
  },
  PublicContentDistribution: {
    Type: 'AWS::CloudFront::Distribution',
    Properties: {
      DistributionConfig: {
        Origins: [
          {
            DomainName: '${self:provider.environment.public_content_bucket_name}.s3.${self:provider.region}.amazonaws.com',
            Id: 'PublicContentBucket',
            CustomOriginConfig: {
              HTTPPort: 80,
              HTTPSPort: 443,
              OriginProtocolPolicy: 'https-only',
            },
          },
        ],
        Enabled: 'true',
        PriceClass: 'PriceClass_100',
        DefaultCacheBehavior: {
          AllowedMethods: ['GET', 'HEAD', 'OPTIONS'],
          TargetOriginId: 'PublicContentBucket',
          CachePolicyId: {
            Ref: 'DistributionCachePolicy',
          },
          ViewerProtocolPolicy: 'https-only',
        },
      },
    },
  },
}

export const Outputs = {
  UserPoolId: {
    Description: 'ID of the User Pool',
    Value: {
      Ref: 'CognitoUserPool',
    },
    Export: {
      Name: '${self:service}-${self:provider.stage}-UserPoolId',
    },
  },
  UserPoolClientId: {
    Description: 'ID of the User Pool Client',
    Value: {
      Ref: 'UserPoolClient',
    },
    Export: {
      Name: '${self:service}-${self:provider.stage}-UserPoolClientId',
    },
  },
  ProductsTableStreamArn: {
    Description: 'Products table stream arn',
    Value: {
      'Fn::GetAtt': ['ProductsTable', 'StreamArn'],
    },
    Export: {
      Name: '${self:service}-${self:provider.stage}-ProductsTableStreamArn',
    },
  },
}
