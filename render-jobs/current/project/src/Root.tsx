import React from 'react';
import {Composition} from 'remotion';
import data from './scenes.json';
import {HomepageVideo} from './HomepageVideo';
export const Root=()=> <Composition id="CodebaseVideoHomepage" component={HomepageVideo} fps={30} width={1920} height={1080} durationInFrames={Math.ceil(data.totalSeconds*30)}/>;
