import { Composition } from 'remotion';
import { ChatVideo, FPS } from './Video';
import beats from './beats.json';

const total = beats.reduce(
  (a: number, b: any) => a + Math.ceil((b.dur + 0.4) * FPS), 0
);

export const RemotionRoot = () => (
  <Composition
    id="MuskChat"
    component={ChatVideo}
    durationInFrames={total}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{ beats }}
  />
);
