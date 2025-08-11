import * as cheerio from 'cheerio';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const pdf = require('pdf-parse');
import 'dotenv/config'
const SYSTEM_PROMPT = `
You are a single-purpose AI agent. Your mission is to find the specific answer to the user's initial question and nothing else.

You have one tool: \`fetch_url_content\`.
- To use it, respond with: \`{"tool_call": {"name": "fetch_url_content", "args": {"url": "URL_TO_FETCH"}}}\`
- After the tool is used, you will get the result back as an \`Observation\`.

Your reasoning process is a loop:
1. Examine all observations.
2. If you have the final answer to the user's original question, you MUST stop and provide it using the \`output\` state.
3. If you need more information to find the final answer, you MUST use the \`tool_call\` to get it.

**CRITICAL RULES FOR OUTPUT:**
- The \`output\` state is ONLY for the final, concrete data requested (e.g., a flight number like "HR-2077", not a sentence about it).
- An output is WRONG if it contains words like "the next step is", "you should call", "the landmark is", or any form of explanation or instruction.
- If your reasoning leads you to a new URL, you MUST call it with the tool. Do not describe it in the output.
`;
const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
if (!GOOGLE_API_KEY) {
    throw new Error("FATAL ERROR: GOOGLE_API_KEY environment variable not found.");
}
const MODEL_NAME = "gemini-1.5-flash-latest";
const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${GOOGLE_API_KEY}`;
async function fetchUrlContent(url) {
    let extractedText = "";
    try {
        const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' };
        const response = await fetch(url, { headers });
        if (!response.ok) { throw new Error(`HTTP request failed with status ${response.status}`); }
        const contentType = response.headers.get('content-type')?.toLowerCase() || '';
        if (contentType.includes('application/pdf')) {
            const pdfBuffer = Buffer.from(await response.arrayBuffer());
            const data = await pdf(pdfBuffer);
            extractedText = data.text;
        } else if (contentType.includes('text/html')) {
            const htmlContent = await response.text();
            const $ = cheerio.load(htmlContent);
            extractedText = $('body').text() || '';
        } else if (contentType.includes('application/json')) {
            const jsonData = await response.json();
            extractedText = JSON.stringify(jsonData, null, 2);
        } else {
            const htmlContent = await response.text();
            const $ = cheerio.load(htmlContent);
            extractedText = $('body').text() || '';
        }
        if (!extractedText.trim()) { return "The document was processed, but no text content could be extracted."; }
    } catch (error) {
        return `Error: An unexpected error occurred while processing the document: ${error.message}`;
    }
    return extractedText;
}
function extractJsonObjects(text) {
    const jsonObjects = [];
    let braceStack = [];
    let startIndex = -1;
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char === '{') {
            if (braceStack.length === 0) { startIndex = i; }
            braceStack.push('{');
        } else if (char === '}') {
            if (braceStack.length > 0) {
                braceStack.pop();
                if (braceStack.length === 0 && startIndex !== -1) {
                    const jsonStr = text.substring(startIndex, i + 1);
                    try { jsonObjects.push(JSON.parse(jsonStr)); } catch (e) { /* Ignore */ }
                    startIndex = -1;
                }
            }
        }
    }
    return jsonObjects;
}
async function handleAgenticWorkflow(documentUrl, question) {
    const messages = [
        { role: "user", parts: [{ text: `${documentUrl} , ${question}` }] }
    ];
    while (true) {
        const payload = {
            contents: messages,
            systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
            generationConfig: { "temperature": 0.1, }
        };
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!response.ok) { throw new Error(`API request failed: ${await response.text()}`); }
        const data = await response.json();
        const rawContent = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!rawContent) { throw new Error("Could not find generated text in the API response."); }
        let jsonChunks = [];
        try {
            jsonChunks.push(JSON.parse(rawContent));
        } catch (e) {
            jsonChunks = extractJsonObjects(rawContent);
        }
        
        if (jsonChunks.length === 0) {
            if (rawContent && !rawContent.includes('{') && rawContent.length < 100) {
                return rawContent;
            }
            throw new Error(`No valid JSON in AI output: ${rawContent}`);
        }
        let actionExecuted = false;
        for (const content of jsonChunks) {
            if (content.output) {
                const isInstruction = /call:|GET|http|instruction|step/i.test(content.output);
                if (isInstruction) {
                    console.warn("AGENT: AI provided a premature output. Forcing self-correction.");
                    messages.push({
                        role: "user",
                        parts: [{ text: `Correction: Your last response was an instruction, not the final answer. You must execute the step you just described using a \`tool_call\`. Do not output instructions.`}]
                    });
                    actionExecuted = true;
                    break; 
                } else {
                    return content.output;
                }
            }
            if (content.tool_call) {
                const toolCall = content.tool_call;
                const funcName = toolCall.name;
                const url = toolCall.args?.url;
                if (funcName === 'fetch_url_content' && url) {
                    const observationText = await fetchUrlContent(url);
                    messages.push({
                        role: "user",
                        parts: [{ text: `Observation: The content of the URL ${url} is:\n\n${observationText}` }]
                    });
                    actionExecuted = true;
                    break; 
                }
            }
        }
        if (!actionExecuted) {
            throw new Error("The AI did not produce a valid action or output.");
        }
    }
}
async function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error("Usage: node agent.js <document_url> \"<question>\"");
        process.exit(1);
    }
    const [url, question] = args;
    try {
        const answer = await handleAgenticWorkflow(url, question);
        console.log(answer); 
    } catch (error) {
        console.error("The agentic workflow failed:", error);
        process.exit(1); 
    }
}
main();