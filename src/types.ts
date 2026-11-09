export type Settings={schema:number;followPointer:boolean;petting:boolean;mascotSize:number;language:'tr'|'en';theme:'light'|'dark'|'system'|'contrast';scale:number;textSize:number;font:'system'|'readable'|'dyslexic';lineHeight:number;letterSpacing:number;accent:string;density:'comfortable'|'compact';motion:boolean;sound:boolean;gamification:boolean;companion:boolean;channel:'stable'|'beta'};
export type Reply={ok:boolean;data?:any;error?:string};
declare global {interface Window {aion?:{invoke:(command:string,payload?:any)=>Promise<Reply>}}}
