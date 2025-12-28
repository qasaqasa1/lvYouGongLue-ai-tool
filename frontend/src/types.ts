export type OutlineNode = {
  id: string;
  title: string;
  level: number;
  children: OutlineNode[];
};

export type OutlineResponse = {
  location: string;
  outline: OutlineNode[];
};
