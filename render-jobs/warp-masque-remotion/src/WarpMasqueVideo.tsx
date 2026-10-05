import React from 'react';
import {AbsoluteFill,Audio,Easing,interpolate,spring,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import sceneData from './scenes.json';
import cues from './cues.json';

type Scene=(typeof sceneData.scenes)[number];
const P={bg:'#06101d',panel:'#0d1b2a',text:'#f8fbff',muted:'#9db0c5',cyan:'#68e1fd',blue:'#6aa9ff',violet:'#a68cff',green:'#6ee7b7',amber:'#fbbf77',line:'#28425d'};

const Box=({label,sub,accent=P.cyan,width=270}:{label:string;sub?:string;accent?:string;width?:number})=>(
  <div style={{width,minHeight:112,border:`1px solid ${accent}66`,borderRadius:24,background:'rgba(13,27,42,.92)',boxShadow:`0 0 42px ${accent}16`,padding:'22px 24px',display:'flex',flexDirection:'column',justifyContent:'center'}}>
    <div style={{fontSize:29,fontWeight:760,lineHeight:1.18}}>{label}</div>
    {sub?<div style={{fontSize:20,color:P.muted,marginTop:8,lineHeight:1.35}}>{sub}</div>:null}
  </div>
);
const Arrow=({label}:{label?:string})=><div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:6,minWidth:80}}>{label?<div style={{fontSize:15,color:P.muted}}>{label}</div>:null}<div style={{fontSize:43,color:P.cyan}}>→</div></div>;
const Pill=({children,accent=P.blue}:{children:React.ReactNode;accent?:string})=><div style={{padding:'10px 16px',borderRadius:999,border:`1px solid ${accent}55`,background:`${accent}12`,fontSize:20,color:'#dbeafe'}}>{children}</div>;

const Architecture=()=> <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:24,width:'100%'}}>
  <Box label="GitHub Actions" sub="注册 / 登录 / 获取短期凭据" accent={P.violet}/><Arrow label="离线材料"/><Box label="config.js" sub="配置编译器" accent={P.amber}/><Arrow label="YAML"/><Box label="Cloudflare Worker" sub="鉴权 / KV / 按需刷新" accent={P.cyan}/><Arrow label="订阅"/><Box label="mihomo Alpha" sub="客户端消费配置" accent={P.green}/>
</div>;

const Pipeline=()=> <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:18,width:'100%'}}>
  <Box label="workflow_dispatch" sub="手动触发" width={230}/><Arrow/><Box label="usque register" sub="注册 WARP 设备" width={245} accent={P.violet}/><Arrow/><Box label="gen_masque.py" sub="展开 MASQUE 节点" width={245} accent={P.amber}/><Arrow/><Box label="mihomo -t" sub="Alpha 配置校验" width={230} accent={P.cyan}/><Arrow/><Box label="artifact" sub="YAML / 链接 / config" width={230} accent={P.green}/>
</div>;

const Math57=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:40}}>
  <div style={{display:'flex',alignItems:'center',gap:22,fontWeight:800}}><div style={{fontSize:104,color:P.cyan}}>8</div><div style={{fontSize:66,color:P.muted}}>×</div><div style={{fontSize:104,color:P.violet}}>7</div><div style={{fontSize:66,color:P.muted}}>+</div><div style={{fontSize:104,color:P.amber}}>1</div><div style={{fontSize:66,color:P.muted}}>=</div><div style={{fontSize:138,color:P.green}}>57</div></div>
  <div style={{display:'flex',gap:14}}><Pill accent={P.cyan}>4 × IPv4</Pill><Pill accent={P.violet}>4 × IPv6</Pill><Pill accent={P.amber}>7 个端口</Pill><Pill accent={P.green}>+ 官方 SNI</Pill></div>
  <div style={{fontSize:25,color:P.muted}}>57 个入口 ≠ 57 个账号；它们共享同一份 WARP 身份</div>
</div>;

const WorkerFlow=()=> <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:30,width:'100%'}}>
  <div style={{display:'flex',alignItems:'center',gap:18}}><Box label="Client" sub="GET /sub" width={210}/><Arrow/><Box label="Worker" sub="验证 token" width={245} accent={P.cyan}/><Arrow/><Box label="KV" sub="config:yaml / state" width={245} accent={P.violet}/></div>
  <div style={{fontSize:34,color:P.muted}}>缓存新鲜？ <span style={{color:P.green}}>直接返回</span> · 过期？ <span style={{color:P.amber}}>进入 rebuild</span></div>
  <div style={{display:'flex',alignItems:'center',gap:16}}><Box label="WARP" sub="复用设备" width={210}/><Box label="Opera" sub="重新刷新" width={210}/><Box label="Proton / Windscribe" sub="读取已推送凭据" width={280}/><Arrow/><Box label="buildConfig()" sub="重新编译 YAML" width={265} accent={P.amber}/></div>
</div>;

const Providers=()=> <div style={{display:'flex',gap:26,justifyContent:'center',width:'100%'}}>
  {[
    ['Opera','Worker 直接刷新','匿名 API 可在 Worker 环境工作',P.cyan],
    ['Proton','GitHub Actions 登录','官方 Python Core + WireGuard 凭据',P.violet],
    ['Windscribe','GitHub Actions 开户','共享出口 IP 容易被降额',P.amber]
  ].map(([a,b,c,d])=><div key={String(a)} style={{width:420,minHeight:285,border:`1px solid ${d}66`,borderRadius:28,background:'rgba(13,27,42,.94)',padding:30}}>
    <div style={{fontSize:42,fontWeight:800,color:String(d)}}>{a}</div><div style={{fontSize:28,fontWeight:700,marginTop:18}}>{b}</div><div style={{fontSize:23,lineHeight:1.5,color:P.muted,marginTop:16}}>{c}</div>
  </div>)}
</div>;

const Security=()=> <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:16,width:'100%'}}>
  <Box label="Password" width={210}/><Arrow/><Box label="PBKDF2-SHA256" sub="随机盐 · 100k" width={285} accent={P.violet}/><Arrow/><Box label="KV hash" width={210} accent={P.cyan}/><Arrow/><Box label="HMAC token" sub="改密码 → 旧 token 失效" width={310} accent={P.green}/>
</div>;

const Compiler=()=> <div style={{display:'grid',gridTemplateColumns:'1fr 360px 1fr',alignItems:'center',gap:32,width:'100%'}}>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>{['WARP','Opera','Proton','Windscribe'].map((x,i)=><Box key={x} label={x} sub="线路原材料" width={250} accent={[P.cyan,P.green,P.violet,P.amber][i]}/>)}</div>
  <div style={{height:300,border:`2px solid ${P.amber}88`,borderRadius:34,background:`${P.amber}10`,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:46,fontWeight:850,color:P.amber}}>config.js</div><div style={{fontSize:23,color:P.muted,marginTop:12}}>compiler core</div></div>
  <div style={{display:'flex',flexDirection:'column',gap:16}}>{['proxies','proxy-groups','DNS / rules','dialer-proxy'].map(x=><Box key={x} label={x} sub="mihomo YAML" width={280} accent={P.blue}/>)}</div>
</div>;

const Recap=()=> <div style={{display:'flex',alignItems:'stretch',justifyContent:'center',gap:26,width:'100%'}}>
  <Box label="GitHub Actions" sub="offline acquisition" width={360} accent={P.violet}/><Box label="Cloudflare Worker" sub="online control plane" width={360} accent={P.cyan}/><Box label="config.js" sub="configuration compiler" width={360} accent={P.amber}/>
</div>;

const Visual=({scene}:{scene:Scene})=>{
  switch(scene.kind){case'architecture':return <Architecture/>;case'pipeline':return <Pipeline/>;case'math':return <Math57/>;case'worker':return <WorkerFlow/>;case'providers':return <Providers/>;case'security':return <Security/>;case'compiler':return <Compiler/>;default:return <Recap/>;}
};

const Caption=({time}:{time:number})=>{
  const active=[...cues].reverse().find(c=>time>=c.start&&time<=c.end+0.06);
  if(!active)return null;
  return <div style={{position:'absolute',left:210,right:210,bottom:58,display:'flex',justifyContent:'center'}}><div style={{maxWidth:1450,padding:'14px 28px 16px',borderRadius:18,background:'rgba(0,0,0,.72)',boxShadow:'0 10px 34px rgba(0,0,0,.3)',fontSize:34,lineHeight:1.35,fontWeight:650,textAlign:'center',textShadow:'0 2px 6px #000'}}>{active.text}</div></div>;
};

export const WarpMasqueVideo=()=>{
  const frame=useCurrentFrame();
  const {fps,durationInFrames}=useVideoConfig();
  const time=frame/fps;
  const found=sceneData.scenes.findIndex(s=>time>=s.start&&time<s.end);
  const scene=sceneData.scenes[found<0?sceneData.scenes.length-1:found];
  const localFrame=Math.max(0,Math.round((time-scene.start)*fps));
  const enter=spring({frame:localFrame,fps,config:{damping:18,stiffness:110,mass:.9}});
  const fadeOut=interpolate(time,[scene.end-.45,scene.end],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.ease)});
  const opacity=enter*fadeOut;
  const y=interpolate(enter,[0,1],[28,0]);
  const progress=frame/Math.max(1,durationInFrames-1);

  return <AbsoluteFill style={{background:P.bg,color:P.text,fontFamily:'"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",system-ui,sans-serif'}}>
    <Audio src={staticFile('narration.mp3')}/>
    <div style={{position:'absolute',inset:0,backgroundImage:'linear-gradient(rgba(104,225,253,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(104,225,253,.045) 1px, transparent 1px)',backgroundSize:'54px 54px'}}/>
    <div style={{position:'absolute',width:760,height:760,borderRadius:999,background:'radial-gradient(circle, rgba(104,225,253,.10), transparent 68%)',right:-180,top:-260}}/>
    <div style={{position:'absolute',left:0,top:0,height:6,width:`${progress*100}%`,background:`linear-gradient(90deg,${P.cyan},${P.violet})`}}/>
    <div style={{position:'absolute',left:94,right:94,top:70,bottom:150,display:'flex',flexDirection:'column',opacity,transform:`translateY(${y}px)`}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><div style={{fontSize:23,letterSpacing:2.4,color:P.cyan,fontWeight:760}}>{scene.kicker}</div><div style={{fontSize:22,color:P.muted}}>WARP MASQUE ACTIONS · {String(scene.index+1).padStart(2,'0')} / 08</div></div>
      <div style={{fontSize:64,fontWeight:850,lineHeight:1.12,marginTop:18,letterSpacing:-1.5}}>{scene.title}</div>
      <div style={{fontSize:26,color:P.muted,marginTop:14}}>{scene.subtitle}</div>
      <div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'center',marginTop:24}}><Visual scene={scene}/></div>
      <div style={{display:'flex',gap:12,alignItems:'center',flexWrap:'wrap'}}><span style={{fontSize:18,color:P.muted,marginRight:4}}>EVIDENCE</span>{scene.evidence.map(e=><span key={e} style={{fontSize:18,color:'#c9d6e3',border:`1px solid ${P.line}`,borderRadius:10,padding:'7px 10px',background:'rgba(13,27,42,.72)'}}>{e}</span>)}</div>
    </div>
    <Caption time={time}/>
  </AbsoluteFill>;
};
