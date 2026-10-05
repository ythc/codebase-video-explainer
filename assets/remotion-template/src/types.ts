export type Evidence = {
  path: string;
  symbol?: string;
};

export type StoryboardScene = {
  id: string;
  title: string;
  purpose?: string;
  duration_seconds: number;
  narration?: string;
  visual_type?: string;
  visuals?: string[];
  animation?: string;
  evidence?: Evidence[];
  code_excerpts?: Array<{
    path: string;
    symbol?: string;
    reason?: string;
  }>;
};

export type Storyboard = {
  title: string;
  language?: string;
  audience?: string;
  target_duration_seconds?: number;
  scenes: StoryboardScene[];
};
