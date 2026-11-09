import React,{useEffect,useRef,useState} from 'react';
import {Pause,Play} from 'lucide-react';
export type AionState='idle'|'read'|'repair'|'celebrate'|'help'|'game';
const rows:Record<AionState,number>={idle:0,read:1,repair:2,celebrate:3,help:4,game:5};
export function Aion({state,motion,label,pause,play}:{state:AionState;motion:boolean;label:string;pause:string;play:string}){
 const [frame,setFrame]=useState(0),[clip,setClip]=useState<AionState>(state),[paused,setPaused]=useState(false),[visible,setVisible]=useState(true),[foreground,setForeground]=useState(!document.hidden),[reduced,setReduced]=useState(matchMedia('(prefers-reduced-motion: reduce)').matches);
 const ref=useRef<HTMLDivElement>(null),successPlayed=useRef(false);
 useEffect(()=>{if(state!=='celebrate')successPlayed.current=false;},[state]);
 useEffect(()=>{const media=matchMedia('(prefers-reduced-motion: reduce)');const change=()=>setReduced(media.matches);const visibility=()=>setForeground(!document.hidden);media.addEventListener('change',change);document.addEventListener('visibilitychange',visibility);const observer=new IntersectionObserver(entries=>setVisible(entries[0]?.isIntersecting??false));if(ref.current)observer.observe(ref.current);return()=>{media.removeEventListener('change',change);document.removeEventListener('visibilitychange',visibility);observer.disconnect();};},[]);
 const animate=motion&&!paused&&!reduced&&visible&&foreground;
 useEffect(()=>{
  setFrame(0);setClip(state==='celebrate'&&successPlayed.current?'idle':state);if(!animate||state==='celebrate'&&successPlayed.current)return;let tick=0;
  const timer=setInterval(()=>{tick++;if(state==='celebrate'&&tick>=4){successPlayed.current=true;setClip('idle');setFrame(0);return;}setFrame(state==='idle'?[0,0,0,1,2,0,3,0][tick%8]:state==='celebrate'?tick:tick%4);},state==='idle'?420:state==='celebrate'?360:380);
  return()=>clearInterval(timer);
 },[state,animate]);
 return <div className="companion-art" ref={ref}><div className="aion-halo"/><div className="aion-sprite" role="img" aria-label={label} data-frame={frame} data-clip={clip} data-animated={animate} style={{backgroundImage:'url(./assets/aion-optimizer.png)',backgroundSize:'400% 600%',backgroundPosition:`${frame/3*100}% ${rows[clip]/5*100}%`}}/><button className="icon-button pause" aria-label={paused?play:pause} onClick={()=>setPaused(p=>!p)}>{paused?<Play size={16}/>:<Pause size={16}/>}</button></div>;
}
