#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

const EVIDENCE = new Set(["OBSERVED","SOURCE_VERIFIED","TESTED","INFERRED","UNTESTED","FAILED","UNSUPPORTED","SUPERSEDED"]);

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function unique(values) {
  return new Set(values).size === values.length;
}

export function canonicalize(value) {
  if (Array.isArray(value)) return "[" + value.map(canonicalize).join(",") + "]";
  if (isObject(value)) {
    return "{" + Object.keys(value).sort().map(key => JSON.stringify(key) + ":" + canonicalize(value[key])).join(",") + "}";
  }
  return JSON.stringify(value);
}

export function sha256(value) {
  return createHash("sha256").update(typeof value === "string" ? value : canonicalize(value)).digest("hex");
}

function checkEvidence(doc, errors) {
  if ("evidence_status" in doc && !EVIDENCE.has(doc.evidence_status)) errors.push("evidence_status is not governed");
}

function validateIntake(doc, errors, warnings) {
  if (doc.intake_id?.match(/^[a-z][a-z0-9-]{2,63}$/) === null) errors.push("intake_id is invalid");
  if (doc.system_owners?.experience !== "Frontage Foundry") errors.push("experience owner must be Frontage Foundry");
  if (doc.system_owners?.implementation !== "Website Foundry") errors.push("implementation owner must be Website Foundry");
  if (doc.system_owners?.processing !== "Server Foundry") errors.push("processing owner must be Server Foundry");
  if (doc.scope_gate?.before_personal_information !== true) errors.push("scope gate must precede personal information");
  if (!Array.isArray(doc.fields) || doc.fields.length === 0) errors.push("fields must be non-empty");
  const fields = Array.isArray(doc.fields) ? doc.fields : [];
  const fieldIds = fields.map(field => field.id);
  if (!unique(fieldIds)) errors.push("field ids collide");
  for (const field of fields) {
    for (const key of ["id","label","purpose","necessity","retention_class"]) if (!field[key]) errors.push("field is missing " + key);
    if (!Array.isArray(field.usual_disclosures)) errors.push("field " + field.id + " must declare usual_disclosures");
    if (field.sensitivity === "sensitive" || field.sensitivity === "high-risk") warnings.push("field " + field.id + " requires a specialist collection-risk review");
  }
  const steps = Array.isArray(doc.steps) ? doc.steps : [];
  if (!unique(steps.map(step => step.id))) errors.push("step ids collide");
  const used = new Set();
  for (const step of steps) {
    if (!Array.isArray(step.field_ids) || step.field_ids.length === 0) errors.push("step " + step.id + " has no fields");
    for (const id of step.field_ids || []) {
      if (!fieldIds.includes(id)) errors.push("step " + step.id + " references unknown field " + id);
      used.add(id);
    }
    if (step.recovery?.preserve_answers !== true || step.recovery?.error_summary !== true || step.recovery?.field_error !== true) errors.push("step " + step.id + " lacks complete recovery");
  }
  for (const id of fieldIds) if (!used.has(id)) errors.push("field " + id + " is not assigned to a step");
  if (!["before_collection","at_collection"].includes(doc.privacy_notice?.timing)) errors.push("privacy notice must appear at or before collection");
  for (const key of ["identity","contact","collection_circumstances","purposes","consequences","usual_disclosures","privacy_policy_url","overseas_disclosures"]) {
    if (doc.privacy_notice?.[key] === undefined) errors.push("privacy notice is missing " + key);
  }
  if (doc.review?.enabled !== true || doc.review?.change_each_answer !== true) errors.push("review-and-change is mandatory");
  if (doc.confirmation?.reference !== true || !doc.confirmation?.next_step || !doc.confirmation?.response_window || !doc.confirmation?.correction_route) errors.push("confirmation is incomplete");
  if (doc.human_handoff?.available !== true) errors.push("human handoff is mandatory");
  const marketing = doc.marketing_consent || {};
  if (marketing.separate_from_service !== true || marketing.optional !== true || marketing.default_selected !== false || marketing.records_when_and_how !== true || !marketing.unsubscribe_route) errors.push("marketing consent contract is unsafe or incomplete");
  if (doc.accessibility_target !== "WCAG 2.2 Level AA") errors.push("accessibility target must be explicit");
  if (!Array.isArray(doc.instrumentation?.events) || !unique(doc.instrumentation.events)) errors.push("instrumentation events must be a unique array");
}

function validateArt(doc, errors, warnings) {
  if (doc.system_owners?.direction !== "Frontage Foundry") errors.push("art direction owner must be Frontage Foundry");
  if (doc.system_owners?.implementation !== "Website Foundry") errors.push("art implementation owner must be Website Foundry");
  const concepts = Array.isArray(doc.concepts) ? doc.concepts : [];
  if (concepts.length < 2) errors.push("at least two materially distinct concepts are required");
  if (!unique(concepts.map(item => item.id))) errors.push("concept ids collide");
  if (!concepts.some(item => item.id === doc.selected_concept_id)) errors.push("selected concept does not exist");
  const assets = Array.isArray(doc.assets) ? doc.assets : [];
  if (!unique(assets.map(item => item.id))) errors.push("asset ids collide");
  const largestBudget = doc.performance_budget?.largest_single_asset_bytes;
  for (const asset of assets) {
    if (!asset.source_reference || !asset.rights_state || !asset.semantic_role) errors.push("asset " + asset.id + " lacks provenance or semantic role");
    const text = asset.alternative?.text ?? "";
    const mode = asset.alternative?.mode;
    if (asset.semantic_role === "decorative" && (mode !== "empty" || text !== "")) errors.push("decorative asset " + asset.id + " must have an empty alternative");
    if (asset.semantic_role !== "decorative" && (!text.trim() || mode === "empty")) errors.push("meaningful asset " + asset.id + " lacks an equivalent");
    if (asset.rights_state === "pending") warnings.push("asset " + asset.id + " rights remain pending");
    if (typeof largestBudget === "number" && asset.encoded_bytes > largestBudget) errors.push("asset " + asset.id + " exceeds the single-asset budget");
    const variants = [...(asset.responsive_variants || [])].sort((a,b) => a.min_width - b.min_width);
    if (variants.length === 0 || variants[0].min_width !== 0) errors.push("asset " + asset.id + " responsive coverage must start at zero");
    for (let index=0; index<variants.length; index++) {
      const variant = variants[index];
      if (!variant.focal_point || variant.focal_point.x < 0 || variant.focal_point.x > 1 || variant.focal_point.y < 0 || variant.focal_point.y > 1) errors.push("asset " + asset.id + " has an invalid focal point");
      if (index < variants.length - 1) {
        if (variant.max_width === null) errors.push("asset " + asset.id + " has an unbounded variant before the end");
        if (variants[index+1].min_width !== variant.max_width + 1) errors.push("asset " + asset.id + " has a responsive gap or overlap");
      } else if (variant.max_width !== null) errors.push("asset " + asset.id + " responsive coverage must end unbounded");
    }
  }
  if (doc.motion?.essential_information_equivalent !== true) errors.push("motion needs a non-motion information equivalent");
  if (doc.motion?.used === true && !["replace","pause","remove"].includes(doc.motion?.reduced_motion)) errors.push("motion must define reduced-motion behaviour");
  const widths = (doc.responsive_frames || []).map(frame => frame.width);
  if (!widths.some(width => width <= 360) || !widths.some(width => width >= 768) || !widths.some(width => width >= 1280)) errors.push("responsive review must cover small, medium and large viewports");
}

function validateExperiment(doc, errors) {
  if (doc.pre_registered !== true) errors.push("experiment must be pre-registered");
  const variants = Array.isArray(doc.variants) ? doc.variants : [];
  if (variants.length < 2 || !unique(variants.map(item => item.id))) errors.push("variants must be unique and include control plus treatment");
  const allocation = variants.reduce((sum,item) => sum + (Number(item.allocation) || 0), 0);
  if (Math.abs(allocation - 1) > 1e-9) errors.push("variant allocation must sum to one");
  if (!doc.primary_metric?.name || !doc.primary_metric?.numerator || !doc.primary_metric?.denominator) errors.push("one defined primary metric is required");
  const categories = new Set((doc.guardrails || []).map(item => item.category));
  for (const category of ["accessibility","privacy","complaints","claim-truth","lead-quality","fulfilment"]) if (!categories.has(category)) errors.push("missing " + category + " guardrail");
  const plan = doc.sample_size_plan || {};
  if (!(plan.alpha > 0 && plan.alpha <= 0.2)) errors.push("alpha is outside the accepted planning range");
  if (!(plan.power >= 0.5 && plan.power < 1)) errors.push("power is outside the accepted planning range");
  if (!(plan.minimum_detectable_effect > 0) || !(plan.calculated_per_variant >= 2) || !plan.baseline_source || !plan.method) errors.push("sample-size plan is incomplete");
  if (!(doc.runtime?.minimum_days >= 1) || !doc.runtime?.start_condition || !doc.runtime?.end_condition) errors.push("runtime contract is incomplete");
  if (!doc.stopping_rule || doc.stopping_rule.length < 20) errors.push("stopping rule is not explicit");
  if (doc.decision_rule?.guardrail_veto !== true) errors.push("guardrail veto must be enabled");
}

function validateControlMatrix(doc, errors) {
  const controls = Array.isArray(doc.controls) ? doc.controls : [];
  if (!unique(controls.map(control => control.id))) errors.push("control ids collide");
  for (const control of controls) {
    if (!["BLOCKER","ADVISORY"].includes(control.severity)) errors.push("control " + control.id + " has invalid severity");
    if (!EVIDENCE.has(control.status)) errors.push("control " + control.id + " has invalid evidence state");
    if (!control.owner || !control.criterion || !Array.isArray(control.evidence)) errors.push("control " + control.id + " is incomplete");
  }
}

function validateSourceRegister(doc, errors) {
  const sources = Array.isArray(doc.sources) ? doc.sources : [];
  if (!unique(sources.map(source => source.id))) errors.push("source ids collide");
  for (const source of sources) {
    if (!source.authority || !source.title || !source.role || !String(source.url || "").startsWith("https://")) errors.push("source " + source.id + " is incomplete");
  }
}

export function validateDocument(doc) {
  const errors=[], warnings=[];
  if (!isObject(doc)) return {valid:false,errors:["document must be an object"],warnings};
  checkEvidence(doc, errors);
  switch (doc.schema) {
    case "kex.apex-customer-intake.v1": validateIntake(doc,errors,warnings); break;
    case "kex.apex-art-direction.v1": validateArt(doc,errors,warnings); break;
    case "kex.apex-conversion-experiment.v1": validateExperiment(doc,errors,warnings); break;
    case "kex.apex-control-matrix.v1": validateControlMatrix(doc,errors); break;
    case "kex.apex-source-register.v1": validateSourceRegister(doc,errors); break;
    default: errors.push("unsupported schema discriminator");
  }
  return {valid:errors.length===0,errors,warnings,canonical_sha256:sha256(doc)};
}

export async function validateFiles(paths) {
  const results=[];
  const docs=[];
  for (const path of paths) {
    try {
      const doc=JSON.parse(await readFile(path,"utf8"));
      docs.push({path,doc});
      results.push({path,...validateDocument(doc)});
    } catch (error) {
      results.push({path,valid:false,errors:[error.message],warnings:[]});
    }
  }
  const register=docs.find(item => item.doc.schema === "kex.apex-source-register.v1")?.doc;
  const matrixResult=results.find(item => docs.find(doc => doc.path === item.path)?.doc.schema === "kex.apex-control-matrix.v1");
  const matrix=docs.find(item => item.doc.schema === "kex.apex-control-matrix.v1")?.doc;
  if (register && matrix && matrixResult) {
    const known=new Set(register.sources.map(source => source.id));
    for (const control of matrix.controls) for (const source of control.sources) if (!known.has(source)) matrixResult.errors.push("control " + control.id + " references unknown source " + source);
    matrixResult.valid=matrixResult.errors.length===0;
  }
  return results;
}

function makeValidIntake() {
  return {schema:"kex.apex-customer-intake.v1",intake_id:"project-enquiry",site_id:"keddeh-com",system_owners:{experience:"Frontage Foundry",implementation:"Website Foundry",processing:"Server Foundry"},scope_gate:{before_personal_information:true},fields:[{id:"need",label:"What outcome do you need?",purpose:"Route the enquiry to the correct capability",necessity:"Required to assess service fit",retention_class:"enquiry",usual_disclosures:[],sensitivity:"ordinary"}],steps:[{id:"scope",field_ids:["need"],recovery:{preserve_answers:true,error_summary:true,field_error:true}}],privacy_notice:{timing:"before_collection",identity:"Keddeh Systems",contact:"privacy route",collection_circumstances:"Direct website enquiry",purposes:["Respond to enquiry"],consequences:"Cannot respond without the required details",usual_disclosures:[],privacy_policy_url:"https://www.keddeh.com/privacy",overseas_disclosures:{likely:false,countries_or_regions:[]}},review:{enabled:true,change_each_answer:true},confirmation:{reference:true,next_step:"Human review",response_window:"Displayed before submission",correction_route:"Contact support"},human_handoff:{available:true},marketing_consent:{separate_from_service:true,optional:true,default_selected:false,records_when_and_how:true,unsubscribe_route:"unsubscribe"},instrumentation:{events:["start","confirm"]},accessibility_target:"WCAG 2.2 Level AA",evidence_status:"UNTESTED"};
}

function makeValidArt() {
  return {schema:"kex.apex-art-direction.v1",system_owners:{direction:"Frontage Foundry",implementation:"Website Foundry"},concepts:[{id:"a"},{id:"b"}],selected_concept_id:"a",assets:[{id:"map",source_reference:"owner-created",rights_state:"verified",semantic_role:"informative",alternative:{mode:"alt",text:"System estate map"},encoded_bytes:100,responsive_variants:[{min_width:0,max_width:767,focal_point:{x:.5,y:.5}},{min_width:768,max_width:null,focal_point:{x:.5,y:.5}}]}],performance_budget:{largest_single_asset_bytes:200},motion:{used:true,reduced_motion:"replace",essential_information_equivalent:true},responsive_frames:[{width:320},{width:768},{width:1440}],evidence_status:"UNTESTED"};
}

function makeValidExperiment() {
  return {schema:"kex.apex-conversion-experiment.v1",pre_registered:true,variants:[{id:"control",allocation:.5},{id:"treatment",allocation:.5}],primary_metric:{name:"qualified completion",numerator:"qualified completions",denominator:"eligible starts"},guardrails:["accessibility","privacy","complaints","claim-truth","lead-quality","fulfilment"].map(category=>({category})),sample_size_plan:{alpha:.05,power:.8,minimum_detectable_effect:.1,calculated_per_variant:100,baseline_source:"observed baseline",method:"two-proportion test"},runtime:{minimum_days:14,start_condition:"instrumentation verified",end_condition:"sample and time reached"},stopping_rule:"Stop only after the minimum sample and runtime are both reached.",decision_rule:{guardrail_veto:true},evidence_status:"UNTESTED"};
}

export function selfTest() {
  const tests=[];
  const record=(name,pass,detail="")=>tests.push({name,pass,detail});
  const intake=makeValidIntake(), art=makeValidArt(), experiment=makeValidExperiment();
  record("unit-valid-intake",validateDocument(intake).valid);
  record("unit-valid-art",validateDocument(art).valid);
  record("unit-valid-experiment",validateDocument(experiment).valid);
  const collision=structuredClone(intake); collision.fields.push({...collision.fields[0]});
  record("collision-field-id",!validateDocument(collision).valid);
  const boundary=structuredClone(art); boundary.assets[0].responsive_variants[1].min_width=700;
  record("boundary-responsive-overlap",!validateDocument(boundary).valid);
  let propertyPass=true;
  for (let n=1;n<10;n++) { const value=structuredClone(experiment); value.variants[0].allocation=n/10; value.variants[1].allocation=1-n/10; propertyPass &&= validateDocument(value).valid; }
  record("property-allocation-partitions",propertyPass);
  const reordered=JSON.parse('{"evidence_status":"UNTESTED","accessibility_target":"WCAG 2.2 Level AA","instrumentation":{"events":["start","confirm"]},"marketing_consent":{"unsubscribe_route":"unsubscribe","records_when_and_how":true,"default_selected":false,"optional":true,"separate_from_service":true},"human_handoff":{"available":true},"confirmation":{"correction_route":"Contact support","response_window":"Displayed before submission","next_step":"Human review","reference":true},"review":{"change_each_answer":true,"enabled":true},"privacy_notice":{"overseas_disclosures":{"countries_or_regions":[],"likely":false},"privacy_policy_url":"https://www.keddeh.com/privacy","usual_disclosures":[],"consequences":"Cannot respond without the required details","purposes":["Respond to enquiry"],"collection_circumstances":"Direct website enquiry","contact":"privacy route","identity":"Keddeh Systems","timing":"before_collection"},"steps":[{"recovery":{"field_error":true,"error_summary":true,"preserve_answers":true},"field_ids":["need"],"id":"scope"}],"fields":[{"sensitivity":"ordinary","usual_disclosures":[],"retention_class":"enquiry","necessity":"Required to assess service fit","purpose":"Route the enquiry to the correct capability","label":"What outcome do you need?","id":"need"}],"scope_gate":{"before_personal_information":true},"system_owners":{"processing":"Server Foundry","implementation":"Website Foundry","experience":"Frontage Foundry"},"site_id":"keddeh-com","intake_id":"project-enquiry","schema":"kex.apex-customer-intake.v1"}');
  record("replay-canonical-hash",sha256(intake)===sha256(reordered));
  const unsafe=structuredClone(intake); unsafe.marketing_consent.default_selected=true;
  record("safety-preselected-marketing",!validateDocument(unsafe).valid);
  const passed=tests.every(test=>test.pass);
  return {passed,tests};
}

const invoked = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (invoked) {
  const args=process.argv.slice(2);
  if (args.includes("--self-test")) {
    const result=selfTest();
    console.log(JSON.stringify(result,null,2));
    process.exitCode=result.passed?0:1;
  } else if (args.length) {
    const results=await validateFiles(args);
    console.log(JSON.stringify(results,null,2));
    process.exitCode=results.every(result=>result.valid)?0:1;
  } else {
    console.error("Usage: node validate-apex-contract.mjs --self-test | <json files...>");
    process.exitCode=2;
  }
}
