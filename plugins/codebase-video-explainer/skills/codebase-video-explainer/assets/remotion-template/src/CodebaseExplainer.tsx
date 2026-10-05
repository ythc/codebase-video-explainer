import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {EvidenceList} from './components/EvidenceList';
import {FlowNodes} from './components/FlowNodes';
import type {Storyboard, StoryboardScene} from './types';

const Scene: React.FC<{scene: StoryboardScene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeIn = interpolate(frame, [0, Math.max(1, fps * 0.4)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const visuals = scene.visuals ?? [];
  const evidence = scene.evidence ?? [];

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #07111f 0%, #111827 55%, #0f172a 100%)',
        color: '#f8fafc',
        fontFamily: 'Inter, system-ui, sans-serif',
        padding: '92px 110px',
      }}
    >
      <div style={{opacity: fadeIn, display: 'flex', height: '100%', flexDirection: 'column'}}>
        <div style={{fontSize: 28, opacity: 0.68, letterSpacing: 1.2}}>CODEBASE EXPLAINER</div>
        <div style={{fontSize: 64, fontWeight: 750, marginTop: 16, lineHeight: 1.12}}>{scene.title}</div>
        {scene.purpose ? (
          <div style={{fontSize: 28, opacity: 0.72, marginTop: 16, maxWidth: 1400}}>{scene.purpose}</div>
        ) : null}

        <div style={{flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          {visuals.length > 0 ? (
            <FlowNodes items={visuals} />
          ) : (
            <div style={{fontSize: 38, opacity: 0.72, textAlign: 'center', maxWidth: 1200}}>
              Replace this fallback scene with project-specific architecture, code, screenshot, or timeline visuals.
            </div>
          )}
        </div>

        <EvidenceList evidence={evidence} />
        <div style={{fontSize: 21, opacity: 0.45, marginTop: 22}}>
          Visual type: {scene.visual_type ?? 'generic'}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const CodebaseExplainer: React.FC<{storyboard: Storyboard}> = ({storyboard}) => {
  const {fps} = useVideoConfig();
  let start = 0;
  return (
    <AbsoluteFill style={{background: '#07111f'}}>
      {storyboard.scenes.map((scene) => {
        const duration = Math.max(1, Math.round(scene.duration_seconds * fps));
        const from = start;
        start += duration;
        return (
          <Sequence key={scene.id} from={from} durationInFrames={duration}>
            <Scene scene={scene} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
