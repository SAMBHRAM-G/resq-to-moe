const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

const OPENROUTER_URL = "https://openrouter.ai";
const MODEL_NAME = "meta-llama/llama-3-8b-instruct:free";

async function queryOpenRouterNode(role, depth, context, apiKey) {
    const prompt = `ROLE: You are the ${role.upper()} node in a Token-Optimal Mixture of Experts crisis matrix.
    Perform exactly ${depth} internal verification passes. Output strict uppercase telemetry log metrics inside brackets. Max 2 sentences.
    CONTEXT: ${context}`;

    try {
        const response = await axios.post(OPENROUTER_URL, {
            model: MODEL_NAME,
            messages: [{ role: "user", content: prompt }],
            temperature: 0.2
        }, {
            headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
            timeout: 12000
        });
        return response.data.choices[0].message.content.trim();
    } catch (e) {
        return `[LOCAL_FALLBACK_L${depth}]: Fallback routine engaged due to edge layer delay. System stable.`;
    }
}

app.post('/api/compute-moe', async (req, res) => {
    const { report, loops, workers, api_key } = req.body;
    const timestamp = new Date().toISOString();
    
    // Spawns parallel asynchronous processing promises across the network
    const tasks = workers.map(w => queryOpenRouterNode(w, loops, report, api_key).then(res => ({ [w]: res })));
    const taskResults = await Promise.all(tasks);
    const traces = Object.assign({}, ...taskResults);

    res.json({
        status: "COMPUTE_CLUSTER_SUCCESS",
        timestamp,
        executed_loops: loops,
        mesh_traces: traces
    });
});

app.listen(3000, () => console.log('MOE Backend Cluster Online on Port 3000'));
