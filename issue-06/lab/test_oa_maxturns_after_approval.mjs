// @openai/agents-core 0.19.0 against 0.20.0: the turn budget after an approval.
//
// #2032 (commit 8567e09, in 0.20.0, 8 Oct 2026): the model call that follows an approval resume
// now counts toward maxTurns. A discharge tool needs approval; the run is paused, serialised with
// RunState.toString(), restored, approved and resumed with maxTurns: 1. Scripted Model object,
// tracing disabled, no API key. The question: the reviewer said yes and the tool ran. What does
// the caller get back?
import { Agent, Runner, tool, RunState, setTracingDisabled, Usage } from '@openai/agents-core';
import { z } from 'zod';
import fs from 'node:fs';
import path from 'node:path';

const pkg = path.join(process.cwd(), 'node_modules/@openai/agents-core/package.json');
const ver = JSON.parse(fs.readFileSync(pkg, 'utf8')).version;
setTracingDisabled(true);

let modelCalls = 0;
const record = [];
const model = {
  async getResponse() {
    modelCalls++;
    const usage = new Usage({ requests: 1, inputTokens: 1, outputTokens: 1, totalTokens: 2 });
    if (modelCalls === 1) {
      return { usage, responseId: 'r1', output: [{ type: 'function_call', id: 'fc1', callId: 'c1', name: 'sign_discharge', arguments: '{"patient_id":"pt-123"}', status: 'completed' }] };
    }
    return { usage, responseId: 'r' + modelCalls, output: [{ type: 'message', id: 'm' + modelCalls, role: 'assistant', status: 'completed', content: [{ type: 'output_text', text: 'Discharge signed.' }] }] };
  },
  async *getStreamedResponse() { throw new Error('streaming not scripted'); },
};

const signDischarge = tool({
  name: 'sign_discharge', description: 'Sign the discharge order.',
  parameters: z.object({ patient_id: z.string() }), needsApproval: true,
  execute: async ({ patient_id }) => { record.push(patient_id); return 'signed'; },
});
const agent = new Agent({ name: 'Discharge', model, tools: [signDischarge] });
const runner = new Runner();

let r = await runner.run(agent, 'Discharge pt-123.', { maxTurns: 1 });
console.log(`@openai/agents-core ${ver}`);
console.log(`  paused: interruptions=${r.interruptions.length} model calls=${modelCalls} writes=${record.length}`);
const state = await RunState.fromString(agent, r.state.toString());
state.approve(state.getInterruptions()[0]);
let outcome;
try {
  r = await runner.run(agent, state, { maxTurns: 1 });
  outcome = `returned finalOutput=${JSON.stringify(r.finalOutput)}`;
} catch (e) {
  outcome = `threw ${e.constructor.name}: ${String(e.message).slice(0, 80)}`;
}
console.log(`  approved and resumed with maxTurns 1: ${outcome}`);
console.log(`  model calls=${modelCalls} writes=${record.length} ${JSON.stringify(record)}`);
console.log(`  SUMMARY ${ver}: approved tool ran ${record.length} time(s); caller ${outcome.startsWith('threw') ? 'got an exception' : 'got a final answer'}`);
