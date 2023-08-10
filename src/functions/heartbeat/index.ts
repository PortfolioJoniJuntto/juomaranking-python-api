import { handlerPath } from "@libs/handlerResolver";
import { AWS } from "@serverless/typescript";

const functions: AWS["functions"] = {
  heartbeat: {
    handler: `${handlerPath(__dirname)}/handler.main`,
    runtime: "nodejs16.x",
    events: [
      {
        httpApi: "GET /heartbeat",
      },
    ],
  },
};

export default functions;
