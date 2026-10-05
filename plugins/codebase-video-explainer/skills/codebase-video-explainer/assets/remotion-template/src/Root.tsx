import React from 'react';
import {Composition} from 'remotion';
import storyboardJson from './storyboard.json';
import {CodebaseExplainer} from './CodebaseExplainer';
import type {Storyboard} from './types';

const FPS = 30;
const storyboard = storyboardJson as Storyboard;
const durationInFrames = Math.max(
  FPS,
  storyboard.scenes.reduce((sum, scene) => sum + Math.max(1, Math.round(scene.duration_seconds * FPS)), 0),
);

export const Root: React.FC = () => {
  return (
    <Composition
      id="CodebaseExplainer"
      component={CodebaseExplainer}
      durationInFrames={durationInFrames}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{storyboard}}
    />
  );
};
