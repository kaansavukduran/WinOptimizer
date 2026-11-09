export type PetPart='head'|'belly'|'tail'|'feet';
export function gazeDirection(x:number,y:number,rect:{left:number;top:number;width:number;height:number}):number|null{
 if(!Number.isFinite(x)||!Number.isFinite(y)||rect.width<=0||rect.height<=0)return null;
 const dx=(x-rect.left-rect.width/2)/(rect.width/2),dy=(y-rect.top-rect.height/2)/(rect.height/2);
 if(Math.hypot(dx,dy)<.15)return null;
 return ((Math.round((Math.atan2(dy,dx)+Math.PI/2)/(2*Math.PI)*16)%16)+16)%16;
}
export function petPart(x:number,y:number):PetPart{return y<.55?'head':y>.86?'feet':x<.27||x>.73?'tail':'belly';}
export function lookCell(direction:number){const n=((Math.round(direction)%16)+16)%16;return {row:9+Math.floor(n/8),column:n%8};}
