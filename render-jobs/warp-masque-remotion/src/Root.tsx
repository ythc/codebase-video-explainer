import {Composition} from 'remotion';
import {WarpMasqueVideo} from './WarpMasqueVideo';
import data from './scenes.json';

const FPS = 30;

export const Root = () => (
  <Composition
    id="WarpMasqueExplainer"
    component={WarpMasqueVideo}
    durationInFrames={Math.ceil(data.totalSeconds * FPS)}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
