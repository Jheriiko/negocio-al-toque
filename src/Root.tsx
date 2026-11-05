import { Composition, CalculateMetadataFunction } from 'remotion';
import { Video } from './Video';

const calculateMetadata: CalculateMetadataFunction<any> = ({ props }) => {
  const scenes = props.scenes || [];
  const totalFrames = scenes.reduce(
    (acc: number, scene: any) => acc + Math.ceil((scene.duration || 5) * 30),
    0
  );
  console.log(`[Root.tsx] Duración calculada: ${totalFrames} frames (${(totalFrames/30).toFixed(2)}s)`);
  return {
    durationInFrames: Math.max(totalFrames, 90),
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
