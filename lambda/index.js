const express = require('express');
const axios = require('axios');
const awsServerlessExpress = require('aws-serverless-express');
const app = express();
app.use(express.json());

const modelEndpoints = {
  'cogvlm-chat-17b': process.env.COGVLM_ENDPOINT,
  'qwenvl-chat': process.env.QWENVL_ENDPOINT,
  // Add more models and their endpoints as necessary
};

app.post('/v1/chat/completions', async (req, res) => {
  const modelName = req.body.model;
  const endpoint = modelEndpoints[modelName];

  if (!endpoint) {
    return res.status(404).send({ error: 'Model not found' });
  }

  try {
    const modelResponse = await axios.post(endpoint, req.body);
    res.json(modelResponse.data);
  } catch (error) {
    res.status(500).send({ error: 'Error forwarding request to model' });
  }
});

const server = awsServerlessExpress.createServer(app);

exports.handler = (event, context) => {
  context.callbackWaitsForEmptyEventLoop = false; // Set to false to speed up successive invocations
  awsServerlessExpress.proxy(server, event, context);
};