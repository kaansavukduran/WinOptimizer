// Reduced support evidence. Event messages and unknown fields never leave through exports.
const FIELDS={readiness:['name','version','build','bootAt','uptimeSeconds','restartSignals','restartUnknown'],defender:['name','mode','serviceEnabled','antivirusEnabled','realtimeEnabled','signatureVersion','signatureAgeDays','signatureAt','rebootRequired'],firewall:['name','enabled','inbound','outbound'],systemEvents:['at','provider','eventId','level','recordId'],appEvents:['at','provider','eventId','level','recordId'],crashes:['at','provider','eventId','level','recordId'],dumps:['name','at','sizeBytes'],updateHistory:['at','name','operation','resultCode','hresult'],services:['name','displayName','state','startMode']};
function reducedCare(report){
 if(!report)return null;
 const safe={schema:report.schema,at:report.at,readOnly:true,online:false,success:report.success,needsAttention:report.needsAttention,eventMessagesOmitted:true,sections:[]};
 for(const section of report.sections||[]){if(!Object.hasOwn(FIELDS,section.id))continue;const items=(section.items||[]).map(row=>Object.fromEntries(FIELDS[section.id].filter(key=>Object.hasOwn(row,key)).map(key=>[key,row[key]])));safe.sections.push({id:section.id,source:section.source,status:section.status,shown:items.length,limited:section.limited===true,items});}
 return structuredClone(safe);
}
function reducedComponent(report){if(!report)return null;return Object.fromEntries(['at','state','restartNeeded','mode','readOnly','online','success','needsAttention'].filter(key=>Object.hasOwn(report,key)).map(key=>[key,report[key]]));}
module.exports={reducedCare,reducedComponent};
