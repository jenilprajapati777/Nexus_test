import React from 'react';
import { HighlightSpan } from '../types';

interface HighlightedTextProps {
  originalText: string;
  highlights: HighlightSpan[];
  onHighlightClick?: (highlight: HighlightSpan) => void;
}

export const HighlightedText: React.FC<HighlightedTextProps> = ({
  originalText,
  highlights,
  onHighlightClick,
}) => {
  if (!originalText) return null;
  if (!highlights || highlights.length === 0) {
    return <span className="font-devanagari text-slate-200">{originalText}</span>;
  }

  // Sort spans by start_char
  const sortedSpans = [...highlights].sort((a, b) => a.start_char - b.start_char);

  const elements: React.ReactNode[] = [];
  let currentIndex = 0;

  sortedSpans.forEach((span, idx) => {
    // Non-highlighted preceding text slice
    if (span.start_char > currentIndex) {
      elements.push(
        <span key={`text-${currentIndex}`} className="font-devanagari text-slate-300">
          {originalText.slice(currentIndex, span.start_char)}
        </span>
      );
    }

    // Highlighted match slice mapped to exact offsets
    const matchedSubstring = originalText.slice(span.start_char, span.end_char);
    elements.push(
      <mark
        key={`highlight-${span.start_char}-${idx}`}
        onClick={() => onHighlightClick && onHighlightClick(span)}
        className="cursor-pointer font-devanagari bg-amber-500/20 text-amber-300 border-b-2 border-amber-400 px-1 py-0.5 rounded font-medium transition-all hover:bg-amber-500/40 hover:text-white"
        title={`Matched via: ${span.matched_type} (${span.matched_term})`}
      >
        {matchedSubstring}
      </mark>
    );

    currentIndex = Math.max(currentIndex, span.end_char);
  });

  // Remaining trailing text slice
  if (currentIndex < originalText.length) {
    elements.push(
      <span key={`text-end`} className="font-devanagari text-slate-300">
        {originalText.slice(currentIndex)}
      </span>
    );
  }

  return <div className="leading-relaxed font-devanagari whitespace-pre-wrap">{elements}</div>;
};
