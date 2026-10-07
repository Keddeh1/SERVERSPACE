import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { canonicalize, sha256, selfTest, validateDocument } from "../tools/validate-apex-contract.mjs";

const root=new URL("../examples/",import.meta.url);
const load=async name=>JSON.parse(await readFile(new URL(name,root),"utf8"));

test("validator deterministic self-test covers unit, collision, boundary, property, replay and safety cases",()=>{
  const result=selfTest();
  assert.equal(result.passed,true,JSON.stringify(result));
  assert.equal(result.tests.length,8);
});

test("reference customer intake is valid",async()=>assert.equal(validateDocument(await load("customer-intake.reference.json")).valid,true));
test("reference art direction is valid",async()=>assert.equal(validateDocument(await load("art-direction.reference.json")).valid,true));
test("reference conversion experiment is valid",async()=>assert.equal(validateDocument(await load("conversion-experiment.reference.json")).valid,true));

test("canonical serialization is independent of object key order",()=>{
  const left={b:2,a:{d:4,c:3}},right={a:{c:3,d:4},b:2};
  assert.equal(canonicalize(left),canonicalize(right));
  assert.equal(sha256(left),sha256(right));
});

test("duplicate field occupancy fails",async()=>{
  const value=await load("customer-intake.reference.json");
  value.fields.push({...value.fields[0]});
  assert.equal(validateDocument(value).valid,false);
});

test("responsive overlap fails",async()=>{
  const value=await load("art-direction.reference.json");
  value.assets[0].responsive_variants[1].min_width=700;
  assert.equal(validateDocument(value).valid,false);
});

test("preselected marketing consent fails",async()=>{
  const value=await load("customer-intake.reference.json");
  value.marketing_consent.default_selected=true;
  assert.equal(validateDocument(value).valid,false);
});
