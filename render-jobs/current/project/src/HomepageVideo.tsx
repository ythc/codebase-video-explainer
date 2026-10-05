import React from 'react';
import {AbsoluteFill,Audio,Easing,interpolate,spring,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import data from './scenes.json';
import cues from './cues.json';

type Scene=(typeof data.scenes)[number];
const C={bg:'#07111f',panel:'#0d1b2a',text:'#f8fafc',muted:'#9eb1c6',cyan:'#67e8f9',blue:'#60a5fa',violet:'#a78bfa',green:'#6ee7b7',amber:'#fbbf77',line:'#28435f'};

const Card=({title,sub,accent=C.cyan,width=300}:{title:string;sub?:string;accent?:string;width?:number})=><div style={{width,minHeight:116,padding:'22px 24px',borderRadius:24,border:`1px solid ${accent}66`,background:'rgba(13,27,42,.94)',boxShadow:`0 0 44px ${accent}14`,display:'flex',flexDirection:'column',justifyContent:'center'}}><div style={{fontSize:28,fontWeight:800}}>{title}</div>{sub?<div style={{fontSize:19,color:C.muted,marginTop:8,lineHeight:1.42}}>{sub}</div>:null}</div>;
const Arrow=()=> <div style={{fontSize:42,color:C.cyan}}>→</div>;
const Chip=({children,accent=C.blue}:{children:React.ReactNode;accent?:string})=><div style={{padding:'10px 15px',borderRadius:999,border:`1px solid ${accent}55`,background:`${accent}12`,fontSize:19}}>{children}</div>;
const Code=({children}:{children:React.ReactNode})=><div style={{fontFamily:'ui-monospace,SFMono-Regular,Menlo,monospace',fontSize:24,background:'#020617',border:`1px solid ${C.line}`,borderRadius:18,padding:'18px 22px',color:'#dbeafe'}}>{children}</div>;

const Intro=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:28}}>
  <div style={{display:'flex',alignItems:'center',gap:18}}><Card title="Local / GitHub Repo" sub="把代码仓库交给 Codex" width={310}/><Arrow/><Card title="Codebase Video Explainer" sub="Codex Plugin + Agent Skill" accent={C.violet} width={390}/><Arrow/><Card title="Developer Explainer MP4" sub="架构 · 执行链路 · 关键代码" accent={C.green} width={340}/></div>
  <div style={{display:'flex',gap:14}}><Chip>Evidence-backed</Chip><Chip accent={C.violet}>Natural Chinese</Chip><Chip accent={C.green}>Remotion</Chip></div>
</div>;

const Install=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:26,width:'100%'}}>
  <Code>codex plugin marketplace add ythc/codebase-video-explainer --ref main</Code>
  <div style={{display:'flex',alignItems:'center',gap:18}}><Card title="codex" sub="启动" width={190}/><Arrow/><Card title="/plugins" sub="打开插件列表" width={230} accent={C.blue}/><Arrow/><Card title="Install plugin" sub="Codebase Video Explainer" width={300} accent={C.violet}/><Arrow/><Card title="New session" sub="开始使用" width={220} accent={C.green}/></div>
</div>;

const Use=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:28}}>
  <Code>分析这个 GitHub 项目，并生成一支中文开发者讲解视频。</Code>
  <div style={{display:'flex',alignItems:'center',gap:16}}><Card title="Scan" sub="仓库与项目清单" width={220}/><Arrow/><Card title="Trace" sub="代表性执行链路" width={230} accent={C.blue}/><Arrow/><Card title="Explain" sub="架构与项目分析" width={230} accent={C.violet}/><Arrow/><Card title="Storyboard" sub="面向开发者的叙事" width={250} accent={C.green}/></div>
</div>;

const Pipeline=()=> <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:13,width:'100%'}}>{['Source','Analysis','Narration','Exact SRT','Remotion','MP4'].map((x,i)=><React.Fragment key={x}><Card title={x} sub={['真实源码','架构 / 链路','Edge TTS','真实语音边界','动画与渲染','最终成片'][i]} accent={[C.cyan,C.blue,C.violet,C.amber,C.green,C.cyan][i]} width={185}/>{i<5?<Arrow/>:null}</React.Fragment>)}</div>;

const Quality=()=> <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:24,width:'100%',maxWidth:1200}}>
  <Card title="Source evidence" sub="关键结论回到真实文件和符号" accent={C.cyan} width={370}/>
  <Card title="A/V sync" sub="检查旁白、字幕和视频时长" accent={C.violet} width={370}/>
  <Card title="Secret-safe" sub="不把密码、Token、私钥和 Cookie 放进输出" accent={C.green} width={370}/>
</div>;

const Recap=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:30}}>
  <Card title="Install once" sub="Codebase Video Explainer" accent={C.cyan} width={500}/>
  <div style={{display:'flex',alignItems:'center',gap:16}}><Card title="Give Codex a repo" sub="Local / GitHub" width={250}/><Arrow/><Card title="Skill does the work" sub="Analyze · Explain · Render · Verify" accent={C.violet} width={350}/><Arrow/><Card title="Get the video" sub="Developer explainer MP4" accent={C.green} width={280}/></div>
</div>;

const Visual=({scene}:{scene:Scene})=>scene.kind==='install'?<Install/>:scene.kind==='use'?<Use/>:scene.kind==='pipeline'?<Pipeline/>:scene.kind==='quality'?<Quality/>:scene.kind==='recap'?<Recap/>:<Intro/>;
const Caption=({time}:{time:number})=>{const cue=[...cues].reverse().find(c=>time>=c.start&&time<=c.end+0.06);if(!cue)return null;return <div style={{position:'absolute',left:185,right:185,bottom:54,display:'flex',justifyContent:'center'}}><div style={{maxWidth:1490,padding:'14px 26px 16px',borderRadius:18,background:'rgba(0,0,0,.74)',fontSize:32,lineHeight:1.36,fontWeight:650,textAlign:'center',textShadow:'0 2px 6px #000'}}>{cue.text}</div></div>};

export const HomepageVideo=()=>{const frame=useCurrentFrame();const {fps,durationInFrames}=useVideoConfig();const time=frame/fps;const idx=data.scenes.findIndex(s=>time>=s.start&&time<s.end);const scene=data.scenes[idx<0?data.scenes.length-1:idx];const local=Math.max(0,Math.round((time-scene.start)*fps));const enter=spring({frame:local,fps,config:{damping:18,stiffness:110,mass:.9}});const fade=interpolate(time,[scene.end-.45,scene.end],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.ease)});const progress=frame/Math.max(1,durationInFrames-1);return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",system-ui,sans-serif'}}><Audio src={staticFile('narration.mp3')}/><div style={{position:'absolute',inset:0,backgroundImage:'linear-gradient(rgba(103,232,249,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(103,232,249,.045) 1px, transparent 1px)',backgroundSize:'54px 54px'}}/><div style={{position:'absolute',width:840,height:840,right:-240,top:-320,borderRadius:999,background:'radial-gradient(circle, rgba(96,165,250,.12), transparent 68%)'}}/><div style={{position:'absolute',left:0,top:0,height:6,width:`${progress*100}%`,background:`linear-gradient(90deg,${C.cyan},${C.violet})`}}/><div style={{position:'absolute',left:92,right:92,top:66,bottom:150,display:'flex',flexDirection:'column',opacity:enter*fade,transform:`translateY(${interpolate(enter,[0,1],[26,0])}px)`}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><div style={{fontSize:22,letterSpacing:2.3,color:C.cyan,fontWeight:800}}>{scene.kicker}</div><div style={{fontSize:21,color:C.muted}}>CODEBASE VIDEO EXPLAINER · {String(scene.index+1).padStart(2,'0')} / 06</div></div><div style={{fontSize:61,fontWeight:850,lineHeight:1.12,marginTop:16,letterSpacing:-1.4}}>{scene.title}</div><div style={{fontSize:25,color:C.muted,marginTop:13}}>{scene.subtitle}</div><div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'center',marginTop:18}}><Visual scene={scene}/></div><div style={{display:'flex',gap:10,alignItems:'center',flexWrap:'wrap'}}><span style={{fontSize:17,color:C.muted,marginRight:4}}>EVIDENCE</span>{scene.evidence.map(e=><span key={e} style={{fontSize:17,color:'#cbd5e1',border:`1px solid ${C.line}`,borderRadius:10,padding:'7px 10px',background:'rgba(13,27,42,.72)'}}>{e}</span>)}</div></div><Caption time={time}/></AbsoluteFill>};
