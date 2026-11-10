const fs=require('node:fs/promises');
function watchProgress(file,callback){let offset=0,reading=false,stopped=false;
 async function read(){if(reading)return;reading=true;try{const text=await fs.readFile(file,'utf8'),lines=text.split('\n');for(;offset<lines.length-1;offset++){try{const event=JSON.parse(lines[offset]);callback({...event,origin:'native'});}catch{}}}catch{}finally{reading=false;}}
 const timer=setInterval(()=>{if(!stopped)void read();},400);
 return async()=>{stopped=true;clearInterval(timer);while(reading)await new Promise(r=>setTimeout(r,10));await read();};
}
module.exports={watchProgress};
