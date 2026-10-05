import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export const FlowNodes: React.FC<{items: string[]}> = ({items}) => {
  const frame = useCurrentFrame();
  const shown = items.slice(0, 6);
  return (
    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22, width: '100%'}}>
      {shown.map((item, index) => {
        const opacity = interpolate(frame, [index * 12, index * 12 + 10], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const translateY = interpolate(frame, [index * 12, index * 12 + 10], [28, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return (
          <React.Fragment key={`${item}-${index}`}>
            {index > 0 ? <div style={{fontSize: 44, opacity: Math.max(0.25, opacity)}}>→</div> : null}
            <div
              style={{
                opacity,
                transform: `translateY(${translateY}px)`,
                minWidth: 180,
                maxWidth: 260,
                padding: '24px 28px',
                borderRadius: 22,
                border: '1px solid rgba(148,163,184,0.45)',
                background: 'rgba(30,41,59,0.82)',
                boxShadow: '0 16px 50px rgba(0,0,0,0.25)',
                textAlign: 'center',
                fontSize: 27,
                lineHeight: 1.25,
              }}
            >
              {item}
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};
