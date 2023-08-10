# RateUp Backend

## Introduction

The backend of RateUp is designed to offer a robust and scalable infrastructure, ensuring seamless operations of the RateUp application. Leveraging the power of AWS services and the Serverless framework, RateUp's backend promises efficiency, security, and scalability.

## Usage

### Deployment

Deploy the serverless application using the following command, replacing placeholders with your specific AWS profile and desired stage:

\```bash
$ npx sls deploy --aws-profile your-aws-profile --stage your_stage
\```

On successful deployment, you'll get an output similar to:

\```bash
Deploying aws-python-http-api-project to stage dev (us-east-1)
...
endpoint: GET - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/
\```

_Note_: Post deployment, your API is accessible publicly. For production deployments, consider configuring an authorizer. Detailed steps can be found in the [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

Invoke the deployed application using HTTP:

\```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/
\```

A successful invocation should yield a response akin to:

\```json
{
"message": "Go Serverless v3.0! Your function executed successfully!",
"input": {
...
}
}
\```

### Local development

For local development, you can use uvicorn:

\```bash
uvicorn main:app --reload
\```

Or invoke your function locally:

\```bash
serverless invoke local --function hello
\```

Emulate API Gateway and Lambda locally using `serverless-offline`:

\```bash
serverless plugin install -n serverless-offline
serverless offline
\```

To explore `serverless-offline` capabilities, check its [GitHub repository](https://github.com/dherault/serverless-offline).

### Bundling dependencies

For 3rd party dependencies, use the `serverless-python-requirements` plugin:

\```bash
serverless plugin install -n serverless-python-requirements
\```

Add dependencies to `requirements.txt` and they'll be auto-injected into the Lambda package during the build. Comprehensive plugin details can be found in its [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).

### Documentation

Access the Swagger Docs at `/dev/docs` or `/docs`.

## Tech Stack

- **AWS**: Cloud services provider offering a broad set of services.
- **Serverless Framework**: A free and open-source framework written using Node.js. Serverless is the first to entirely build applications on Lambda, a serverless computing platform provided by Amazon as a part of Amazon Web Services.

## Support

Encounter any issues, thats bad :(

---

RateUp Backend: Powering seamless app operations and interactions! 🚀💾
