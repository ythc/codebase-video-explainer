import React from 'react';
import {Composition} from 'remotion';
import data from './scenes.json';
import {PluginHomepageVideo} from './PluginHomepageVideo';
export const Root=()=> <Composition id="CodebaseVideoPluginHomepage" component={PluginHomepageVideo} fps={30} width={1920} height={1080} durationInFrames={Math.ceil(data.totalSeconds*30)}/>;
