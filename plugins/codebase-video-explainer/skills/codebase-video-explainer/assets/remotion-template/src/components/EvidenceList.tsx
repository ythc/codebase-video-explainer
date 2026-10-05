import React from 'react';
import type {Evidence} from '../types';

export const EvidenceList: React.FC<{evidence: Evidence[]}> = ({evidence}) => {
  if (evidence.length === 0) return null;
  return (
    <div style={{display: 'flex', gap: 14, flexWrap: 'wrap', justifyContent: 'center'}}>
      {evidence.slice(0, 4).map((item, index) => (
        <div
          key={`${item.path}-${index}`}
          style={{
            fontFamily: 'monospace',
            fontSize: 20,
            padding: '10px 14px',
            borderRadius: 12,
            background: 'rgba(15,23,42,0.75)',
            border: '1px solid rgba(100,116,139,0.35)',
          }}
        >
          {item.path}{item.symbol ? ` :: ${item.symbol}` : ''}
        </div>
      ))}
    </div>
  );
};
