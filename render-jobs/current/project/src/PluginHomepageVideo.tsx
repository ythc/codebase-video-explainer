import React from 'react';
import {AbsoluteFill,Audio,Easing,interpolate,spring,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import scenes from './scenes.json';
import cues from './cues.json';

type Scene=(typeof scenes.scenes)[number];
const C={bg:'#07111f',panel:'#0d1b2a',text:'#f8fafc',muted:'#9eb1c6',cyan:'#67e8f9',blue:'#60a5fa',violet:'#a78bfa',green:'#6ee7b7',amber:'#fbbf77',line:'#28435f'};

const Card=({title,sub,accent=C.cyan,width=300}:{title:string;sub?:string;accent?:string;width?:number})=><div style={{width,minHeight:118,padding:'22px 24px',borderRadius:24,border:`1px solid ${accent}66`,background:'rgba(13,27,42,.94)',boxShadow:`0 0 44px ${accent}14`,display:'flex',flexDirection:'column',justifyContent:'center'}}><div style={{fontSize:28,fontWeight:800}}>{title}</div>{sub?<div style={{fontSize:19,color:C.muted,marginTop:8,lineHeight:1.4}}>{sub}</div>:null}</div>;
const Arrow=()=> <div style={{fontSize:42,color:C.cyan}}>→</div>;
const Chip=({children,accent=C.blue}:{children:React.ReactNode;accent?:string})=><div style={{padding:'10px 15px',borderRadius:999,border:`1px solid ${accent}55`,background:`${accent}12`,fontSize:19}}>{children}</div>;
const Code=({children}:{children:React.ReactNode})=><div style={{fontFamily:'ui-monospace,SFMono-Regular,Menlo,monospace',fontSize:25,background:'#020617',border:`1px solid ${C.line}`,borderRadius:18,padding:'18px 22px',color:'#dbeafe',boxShadow:'0 16px 36px rgba(0,0,0,.24)'}}>{children}</div>;

const Positioning=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:28}}>
  <div style={{display:'flex',alignItems:'center',gap:18}}><Card title="Codex" sub="安装 / 发现 / 调用"/><Arrow/><Card title="Codebase Video Explainer" sub="Skill-only Plugin" accent={C.violet} width={400}/><Arrow/><Card title="Agent Skill" sub="真正执行分析与视频工作流" accent={C.green}/></div>
  <div style={{display:'flex',gap:14}}><Chip>Plugin = 分发单位</Chip><Chip accent={C.violet}>Skill = 能力单位</Chip><Chip accent={C.green}>无需 MCP Server</Chip></div>
</div>;

const Install=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:26,width:'100%'}}>
  <Code>codex plugin marketplace add ythc/codebase-video-explainer --ref main</Code>
  <div style={{display:'flex',alignItems:'center',gap:18}}><Card title="codex" sub="启动 Codex" width={220}/><Arrow/><Card title="/plugins" sub="打开插件浏览器" width={250} accent={C.blue}/><Arrow/><Card title="Install plugin" sub="Codebase Video Explainer" width={300} accent={C.violet}/><Arrow/><Card title="New session" sub="重新发现 Skill" width={250} accent={C.green}/></div>
</div>;

const Structure=()=> <div style={{display:'grid',gridTemplateColumns:'420px 1fr',gap:30,width:'100%',maxWidth:1320,alignItems:'center'}}>
  <div style={{fontFamily:'ui-monospace,SFMono-Regular,Menlo,monospace',fontSize:22,lineHeight:1.55,background:'#020617',border:`1px solid ${C.line}`,borderRadius:22,padding:24}}>
    <div style={{color:C.cyan}}>.agents/plugins/marketplace.json</div>
    <div>plugins/codebase-video-explainer/</div>
    <div style={{paddingLeft:22,color:C.violet}}>plugin.json</div>
    <div style={{paddingLeft:22}}>.codex-plugin/plugin.json</div>
    <div style={{paddingLeft:22,color:C.green}}>skills/codebase-video-explainer/</div>
    <div style={{paddingLeft:44}}>SKILL.md</div>
    <div style={{paddingLeft:44}}>scripts/</div>
    <div style={{paddingLeft:44}}>references/</div>
    <div style={{paddingLeft:44}}>assets/</div>
  </div>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:18}}>
    <Card title="SKILL.md" sub="行为控制入口" accent={C.cyan} width={390}/>
    <Card title="references/" sub="分析 / 分镜 / 制作 / QA" accent={C.blue} width={390}/>
    <Card title="scripts/" sub="确定性辅助工具" accent={C.violet} width={390}/>
    <Card title="assets/" sub="Remotion / Actions 模板" accent={C.amber} width={390}/>
  </div>
</div>;

const Workflow=()=> <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:14,width:'100%'}}>{['Analyze','Architecture','Storyboard','TTS','Exact SRT','Remotion'].map((x,i)=><React.Fragment key={x}><Card title={x} sub={['源码证据','真实执行路径','开发者叙事','整场景语音','SentenceBoundary','最终 MP4'][i]} accent={[C.cyan,C.blue,C.violet,C.amber,C.green,C.cyan][i]} width={190}/>{i<5?<Arrow/>:null}</React.Fragment>)}</div>;

const Render=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:30}}>
  <div style={{display:'flex',alignItems:'center',gap:18}}><Card title="Local Remotion" sub="typecheck → still → render" accent={C.cyan}/><Arrow/><Card title="GitHub Actions Remotion" sub="npm / Chromium 受限时" accent={C.violet} width={360}/><Arrow/><Card title="FFmpeg fallback" sub="最后保底" accent={C.amber}/></div>
  <div style={{display:'flex',gap:14}}><Chip accent={C.green}>真实 remotion render</Chip><Chip>ffprobe 验证</Chip><Chip accent={C.violet}>保留运行 provenance</Chip></div>
</div>;

const Recap=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:30}}>
  <Card title="Codebase Video Explainer" sub="Installable Codex Skill-only Plugin" accent={C.cyan} width={560}/>
  <div style={{display:'flex',alignItems:'center',gap:16}}><Card title="Install once" sub="Codex Plugin" width={230}/><Arrow/><Card title="Give a repo" sub="Local / GitHub" accent={C.blue} width={230}/><Arrow/><Card title="Skill runs" sub="Analyze → Render → QA" accent={C.violet} width={260}/><Arrow/><Card title="Get video" sub="Developer explainer MP4" accent={C.green} width={280}/></div>
</div>;

const Visual=({scene}:{scene:Scene})=>scene.kind==='install'?<Install/>:scene.kind==='structure'?<Structure/>:scene.kind==='workflow'?<Workflow/>:scene.kind==='render'?<Render/>:scene.kind==='recap'?<Recap/>:<Positioning/>;

const Caption=({time}:{time:number})=>{const cue=[...cues].reverse().find(c=>time>=c.start&&time<=c.end+0.06);if(!cue)return null;return <div style={{position:'absolute',left:185,right:185,bottom:54,display:'flex',justifyContent:'center'}}><div style={{maxWidth:1490,padding:'14px 26px 16px',borderRadius:18,background:'rgba(0,0,0,.74)',fontSize:32,lineHeight:1.36,fontWeight:650,textAlign:'center',textShadow:'0 2px 6px #000'}}>{cue.text}</div></div>};

export const PluginHomepageVideo=()=>{const frame=useCurrentFrame();const {fps,durationInFrames}=useVideoConfig();const time=frame/fps;const idx=scenes.scenes.findIndex(s=>time>=s.start&&time<s.end);const scene=scenes.scenes[idx<0?scenes.scenes.length-1:idx];const local=Math.max(0,Math.round((time-scene.start)*fps));const enter=spring({frame:local,fps,config:{damping:18,stiffness:110,mass:.9}});const fade=interpolate(time,[scene.end-.45,scene.end],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.ease)});const progress=frame/Math.max(1,durationInFrames-1);return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",system-ui,sans-serif'}}><Audio src={staticFile('narration.mp3')}/><div style={{position:'absolute',inset:0,backgroundImage:'linear-gradient(rgba(103,232,249,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(103,232,249,.045) 1px, transparent 1px)',backgroundSize:'54px 54px'}}/><div style={{position:'absolute',width:840,height:840,right:-240,top:-320,borderRadius:999,background:'radial-gradient(circle, rgba(96,165,250,.12), transparent 68%)'}}/><div style={{position:'absolute',left:0,top:0,height:6,width:`${progress*100}%`,background:`linear-gradient(90deg,${C.cyan},${C.violet})`}}/><div style={{position:'absolute',left:92,right:92,top:66,bottom:150,display:'flex',flexDirection:'column',opacity:enter*fade,transform:`translateY(${interpolate(enter,[0,1],[26,0])}px)`}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><div style={{fontSize:22,letterSpacing:2.3,color:C.cyan,fontWeight:800}}>{scene.kicker}</div><div style={{fontSize:21,color:C.muted}}>CODEBASE VIDEO EXPLAINER · {String(scene.index+1).padStart(2,'0')} / 06</div></div><div style={{fontSize:61,fontWeight:850,lineHeight:1.12,marginTop:16,letterSpacing:-1.4}}>{scene.title}</div><div style={{fontSize:25,color:C.muted,marginTop:13}}>{scene.subtitle}</div><div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'center',marginTop:18}}><Visual scene={scene}/></div><div style={{display:'flex',gap:10,alignItems:'center',flexWrap:'wrap'}}><span style={{fontSize:17,color:C.muted,marginRight:4}}>EVIDENCE</span>{scene.evidence.map(e=><span key={e} style={{fontSize:17,color:'#cbd5e1',border:`1px solid ${C.line}`,borderRadius:10,padding:'7px 10px',background:'rgba(13,27,42,.72)'}}>{e}</span>)}</div></div><Caption time={time}/></AbsoluteFill>};
