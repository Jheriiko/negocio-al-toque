import { Composition } from 'remotion';
import { Video } from './Video';
export const RemotionRoot = () => (
  <Composition id="TechUcronia" component={Video} durationInFrames={600} fps={30} width={1080} height={1920} />
);
