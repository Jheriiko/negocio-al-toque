import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig, Video as RemotionVideo, Img } from 'remotion';

const FPS = 30;

export const Video = ({ scenes }: { scenes: any[] }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {scenes.map((scene, index) => {
        // Calcular startFrame usando la MISMA fórmula que calculateMetadata
        const startFrame = scenes.slice(0, index).reduce(
          (acc, s) => acc + Math.ceil((s.duration || 5) * FPS), 0
        );
        const durationInFrames = Math.ceil((scene.duration || 5) * FPS);
        return (
          <Sequence
            key={`scene-${index}-${scene.image}`}
            from={startFrame}
            durationInFrames={durationInFrames}
          >
            <SceneComponent scene={scene} index={index} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const SceneComponent = ({ scene, index }: { scene: any; index: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }}>
      {/* Video o imagen - SIEMPRE dentro del mismo Sequence que el audio */}
      {scene.isVideo ? (
        <RemotionVideo
          src={staticFile(scene.image)}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      ) : (
        <Img
          src={staticFile(scene.image)}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      )}

      {/* Audio atado al Sequence. Al terminar el Sequence, el audio se corta con él. */}
      <Audio src={staticFile(scene.audio)} />

      {/* Texto con key única por escena: fuerza remontaje y evita solapamiento */}
      <div
        key={`text-${index}-${scene.text.slice(0, 8)}`}
        style={{
          position: 'absolute',
          bottom: '15%',
          width: '90%',
          backgroundColor: 'rgba(0,0,0,0.78)',
          padding: '20px',
          borderRadius: '15px',
          zIndex: 10,
        }}
      >
        <h1 style={{
          color: '#FFFFFF',
          fontFamily: 'sans-serif',
          fontSize: '45px',
          fontWeight: 'bold',
          textAlign: 'center',
          margin: 0,
          textShadow: '2px 2px 4px #000'
        }}>
          {scene.text}
        </h1>
      </div>
    </AbsoluteFill>
  );
};
