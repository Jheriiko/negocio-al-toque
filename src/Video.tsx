import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, spring, useVideoConfig, Img } from 'remotion';

export const Video = ({ scenes }: { scenes: any[] }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#FFF8E7' }}>
      {scenes.map((scene, index) => {
        const durationInFrames = Math.floor(scene.duration * 30);
        const startFrame = index * durationInFrames;
        return (
          <Sequence key={index} from={startFrame} durationInFrames={durationInFrames}>
            <ComicScene scene={scene} index={index} total={scenes.length} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const ComicScene = ({ scene, index, total }: { scene: any; index: number; total: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const charsToShow = Math.floor(frame / 2);
  const displayedText = scene.text.slice(0, charsToShow);
  const scaleAnim = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const opacityAnim = Math.min(1, frame / 10);

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
      <Img src={staticFile(scene.image)} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: '8px solid #000', boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)', pointerEvents: 'none', zIndex: 10 }} />

      <Audio src={staticFile(scene.audio)} />

      <div style={{ position: 'absolute', top: '20px', left: '20px', zIndex: 20, backgroundColor: '#FFD700', border: '3px solid #000', padding: '5px 15px', borderRadius: '50%', fontFamily: 'Impact, sans-serif', fontSize: '20px', fontWeight: 'bold', boxShadow: '3px 3px 0px #000' }}>
        {index + 1}
      </div>

      <div style={{ width: '90%', zIndex: 20, transform: `scale(${scaleAnim})`, opacity: opacityAnim }}>
        <div style={{ backgroundColor: '#FFFFFF', border: '4px solid #000000', borderRadius: '20px', padding: '30px 25px', boxShadow: '8px 8px 0px rgba(0,0,0,0.8)', position: 'relative' }}>
          <div style={{ position: 'absolute', bottom: '-20px', left: '40px', width: '0', height: '0', borderLeft: '20px solid transparent', borderRight: '20px solid transparent', borderTop: '20px solid #000000' }} />
          <div style={{ position: 'absolute', bottom: '-14px', left: '44px', width: '0', height: '0', borderLeft: '16px solid transparent', borderRight: '16px solid transparent', borderTop: '16px solid #FFFFFF' }} />

          <h1 style={{ color: '#000000', fontFamily: 'Impact, sans-serif', fontSize: '42px', fontWeight: 'bold', lineHeight: 1.2, margin: 0, textAlign: 'center', textTransform: 'uppercase' }}>
            {displayedText}
            <span style={{ color: '#FF0000', opacity: frame % 12 > 6 ? 1 : 0 }}>▌</span>
          </h1>
        </div>
      </div>

      <div style={{ position: 'absolute', bottom: '30px', right: '30px', zIndex: 20, backgroundColor: '#000', color: '#FFD700', padding: '8px 16px', border: '3px solid #FFD700', fontFamily: 'Impact, sans-serif', fontSize: '18px', fontWeight: 'bold', transform: 'rotate(-3deg)' }}>
        NEGOCIO AL TOQUE
      </div>
    </AbsoluteFill>
  );
};
