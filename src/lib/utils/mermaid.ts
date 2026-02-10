import { v4 as uuidv4 } from 'uuid';

let mermaidInstance: typeof import('mermaid').default | null = null;

export const getMermaid = async () => {
  if (!mermaidInstance) {
    const { default: mermaid } = await import('mermaid');
    mermaid.initialize({
      startOnLoad: false,
      theme: document.documentElement.classList.contains('dark') ? 'dark' : 'default',
      securityLevel: 'loose'
    });
    mermaidInstance = mermaid;
  }
  return mermaidInstance;
};

export const renderMermaidDiagram = async (code: string) => {
  const mermaid = await getMermaid();
  const parseResult = await mermaid.parse(code, { suppressErrors: false });
  if (parseResult) {
    const { svg } = await mermaid.render(`mermaid-${uuidv4()}`, code);
    return svg;
  }
  return '';
};
