import { Composition, CalculateMetadataFunction } from 'remotion';
import { Video } from './Video';

const FPS = 30;

const calculateMetadata: CalculateMetadataFunction<any> = ({ props }) => {
  const scenes = props.scenes || [];
  const totalFrames = scenes.reduce((acc: number, scene: any) => {
    return acc + Math.ceil((scene.duration || 5) * FPS);
  }, 0);
  console.log(`[Root.tsx] Total frames: ${totalFrames} (~${(totalFrames/FPS).toFixed(2)}s)`);
  return {
    durationInFrames: Math.max(totalFrames, 90),
    fps: FPS,
    width: 1080,
    height: 1920,
  };
};

export const RemotionRoot = () => (
  <Composition
    id="TechUcronia"
    component={Video}
    durationInFrames={3600}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{ scenes: [] }}
    calculateMetadata={calculateMetadata}
  />
);
