import React,{useEffect,useRef,useState} from 'react';
import {Heart,Pause,Play} from 'lucide-react';
import {gazeDirection,lookCell,petPart,type PetPart} from './aion-interaction.mts';
import {tr,en} from './i18n';
export type AionState='idle'|'read'|'repair'|'celebrate'|'help'|'game';
const rows:Record<AionState,number>={idle:0,read:1,repair:2,celebrate:3,help:4,game:5};
type Preferences={followPointer:boolean;petting:boolean;mascotSize:number};
export function Aion({state,motion,label,pause,play,language='tr',preferences={followPointer:true,petting:true,mascotSize:100}}:{state:AionState;motion:boolean;label:string;pause:string;play:string;language?:'tr'|'en';preferences?:Preferences}){
 const t=language==='tr'?tr:en;
 const [frame,setFrame]=useState(0),[clip,setClip]=useState<AionState>(state),[paused,setPaused]=useState(false),[visible,setVisible]=useState(true),[foreground,setForeground]=useState(!document.hidden),[reduced,setReduced]=useState(matchMedia('(prefers-reduced-motion: reduce)').matches),[direction,setDirection]=useState<number|null>(null),[reaction,setReaction]=useState<{part:PetPart;frame:number}|null>(null),[caption,setCaption]=useState<PetPart|null>(null);
 const ref=useRef<HTMLDivElement>(null),target=useRef<HTMLButtonElement>(null),successPlayed=useRef(false),reactionTimer=useRef<ReturnType<typeof setInterval>|null>(null),captionTimer=useRef<ReturnType<typeof setTimeout>|null>(null);
 useEffect(()=>{if(state!=='celebrate')successPlayed.current=false;},[state]);
 useEffect(()=>{const media=matchMedia('(prefers-reduced-motion: reduce)');const change=()=>setReduced(media.matches);const visibility=()=>setForeground(!document.hidden);media.addEventListener('change',change);document.addEventListener('visibilitychange',visibility);const observer=new IntersectionObserver(entries=>setVisible(entries[0]?.isIntersecting??false));if(ref.current)observer.observe(ref.current);return()=>{media.removeEventListener('change',change);document.removeEventListener('visibilitychange',visibility);observer.disconnect();};},[]);
 const animate=motion&&!paused&&!reduced&&visible&&foreground;
 useEffect(()=>{
  setFrame(0);setClip(state==='celebrate'&&successPlayed.current?'idle':state);if(!animate||state==='celebrate'&&successPlayed.current)return;let tick=0;
  const timer=setInterval(()=>{tick++;if(state==='celebrate'&&tick>=4){successPlayed.current=true;setClip('idle');setFrame(0);clearInterval(timer);return;}setFrame(state==='idle'?[0,0,0,1,2,0,3,0][tick%8]:state==='celebrate'?tick:tick%4);},state==='idle'?420:state==='celebrate'?360:380);
  return()=>clearInterval(timer);
 },[state,animate]);
 useEffect(()=>{
  setDirection(null);if(!animate||!preferences.followPointer||state!=='idle')return;
  let pending=0;let last:{x:number;y:number}|null=null;
  const move=(event:PointerEvent)=>{if(event.pointerType==='touch')return;last={x:event.clientX,y:event.clientY};if(pending)return;pending=requestAnimationFrame(()=>{pending=0;const rect=target.current?.getBoundingClientRect();if(rect&&last)setDirection(gazeDirection(last.x,last.y,rect));});};
  const leave=()=>setDirection(null);
  window.addEventListener('pointermove',move,{passive:true});document.documentElement.addEventListener('pointerleave',leave);window.addEventListener('blur',leave);
  return()=>{window.removeEventListener('pointermove',move);document.documentElement.removeEventListener('pointerleave',leave);window.removeEventListener('blur',leave);cancelAnimationFrame(pending);};
 },[animate,preferences.followPointer,state]);
 useEffect(()=>{if(!preferences.petting||!visible||!foreground||!animate||state==='celebrate'){if(reactionTimer.current)clearInterval(reactionTimer.current);setReaction(null);}},[preferences.petting,visible,foreground,state,animate]);
 useEffect(()=>()=>{if(reactionTimer.current)clearInterval(reactionTimer.current);if(captionTimer.current)clearTimeout(captionTimer.current);},[]);
 function pet(event:React.MouseEvent<HTMLButtonElement>){
  if(!preferences.petting)return;const box=event.currentTarget.getBoundingClientRect();const part=event.detail===0?'head':petPart((event.clientX-box.left)/box.width,(event.clientY-box.top)/box.height);
  if(reactionTimer.current)clearInterval(reactionTimer.current);if(captionTimer.current)clearTimeout(captionTimer.current);setCaption(part);setReaction({part,frame:animate?0:2});captionTimer.current=setTimeout(()=>setCaption(null),1800);
  let next=0;const count=part==='feet'?5:4;reactionTimer.current=setInterval(()=>{next++;if(next>=count){if(reactionTimer.current)clearInterval(reactionTimer.current);setReaction(null);}else if(animate)setReaction({part,frame:next});},animate?180:240);
 }
 const usePet=!!reaction||direction!==null;
 const cell=reaction?{row:reaction.part==='feet'?4:3,column:reaction.frame}:direction!==null?lookCell(direction):{row:rows[clip],column:frame};
 const columns=usePet?8:4,atlasRows=usePet?11:6,cellWidth=usePet?192:256,cellHeight=usePet?208:256;
 const visualClip=reaction?'pet':direction!==null?'look':clip;
 const art=<svg className="aion-sprite" role="img" aria-label={label} viewBox={`0 0 ${cellWidth} ${cellHeight}`} preserveAspectRatio="xMidYMax meet" data-frame={cell.column} data-clip={visualClip} data-app-state={state} data-direction={direction??''} data-pet-part={reaction?.part||''} data-animated={animate} style={{backgroundImage:'none',backgroundPosition:`${cell.column/(columns-1)*100}% ${cell.row/(atlasRows-1)*100}%`}}><image href={usePet?'./assets/aion-pet.png':'./assets/aion-optimizer.png'} x={-cell.column*cellWidth} y={-cell.row*cellHeight} width={columns*cellWidth} height={atlasRows*cellHeight}/></svg>;
 return <div className="companion-art" ref={ref} style={{'--mascot-scale':preferences.mascotSize/100} as React.CSSProperties}><div className="aion-halo"/><button ref={target} type="button" className={`aion-pet-target ${preferences.petting?'interactive':''}`} aria-label={preferences.petting?t.petAion:label} title={preferences.petting?t.petHint:label} onClick={pet} disabled={!preferences.petting}>{art}</button>{caption&&<span className="aion-affection" role="status"><Heart size={15}/>{t[({head:'petHead',belly:'petBelly',tail:'petTail',feet:'petFeet'} as const)[caption]]}</span>}<button className="icon-button pause" aria-label={paused?play:pause} onClick={()=>setPaused(p=>!p)}>{paused?<Play size={16}/>:<Pause size={16}/>}</button></div>;
}
