import { AWS } from '@serverless/typescript'

const functions: AWS['functions'] = {
  imageDownloadHandler: {
    image: 'image-download-handler',
    runtime: 'python3.8',
    timeout: 30,
    events: [
      {
        stream: {
          type: 'dynamodb',
          arn: {
            'Fn::ImportValue': '${self:service}-${self:provider.stage}-ProductsTableStreamArn',
          },
          filterPatterns: [
            {
              eventName: ['INSERT'],
            },
          ],
        },
      },
    ],
  },
}

export default functions
