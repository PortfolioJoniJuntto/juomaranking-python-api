export const main = async (event: any) => {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: `Hello, welcome to the exciting Serverless world!`,
      event,
    }),
  };
};
