interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  const renderMarkdown = (text: string): JSX.Element[] => {
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];
    let currentList: string[] = [];
    let listType: 'ul' | 'ol' | null = null;
    let inCodeBlock = false;
    let codeBlockContent: string[] = [];
    let codeBlockLang = '';

    const flushList = () => {
      if (currentList.length > 0 && listType) {
        const ListTag = listType;
        elements.push(
          <ListTag key={elements.length} className="ml-4 my-2 space-y-1">
            {currentList.map((item, idx) => (
              <li key={idx} className="text-sm" dangerouslySetInnerHTML={{ __html: processInlineMarkdown(item) }} />
            ))}
          </ListTag>
        );
        currentList = [];
        listType = null;
      }
    };

    const flushCodeBlock = () => {
      if (codeBlockContent.length > 0) {
        elements.push(
          <pre key={elements.length} className="bg-gray-800 text-gray-100 p-3 rounded-md my-2 overflow-x-auto">
            <code className={`text-xs ${codeBlockLang ? `language-${codeBlockLang}` : ''}`}>
              {codeBlockContent.join('\n')}
            </code>
          </pre>
        );
        codeBlockContent = [];
        codeBlockLang = '';
      }
    };

    lines.forEach((line, index) => {
      // Handle code blocks
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          flushCodeBlock();
          inCodeBlock = false;
        } else {
          flushList();
          inCodeBlock = true;
          codeBlockLang = line.trim().substring(3).trim();
        }
        return;
      }

      if (inCodeBlock) {
        codeBlockContent.push(line);
        return;
      }

      // Headers
      if (line.startsWith('### ')) {
        flushList();
        elements.push(
          <h3 key={index} className="text-md font-semibold mt-3 mb-1">
            {line.substring(4)}
          </h3>
        );
        return;
      }
      if (line.startsWith('## ')) {
        flushList();
        elements.push(
          <h2 key={index} className="text-lg font-bold mt-3 mb-2">
            {line.substring(3)}
          </h2>
        );
        return;
      }
      if (line.startsWith('# ')) {
        flushList();
        elements.push(
          <h1 key={index} className="text-xl font-bold mt-4 mb-2">
            {line.substring(2)}
          </h1>
        );
        return;
      }

      // Unordered list
      if (line.match(/^[\s]*[-*+]\s+/)) {
        if (listType !== 'ul') {
          flushList();
          listType = 'ul';
        }
        currentList.push(line.replace(/^[\s]*[-*+]\s+/, ''));
        return;
      }

      // Ordered list
      if (line.match(/^[\s]*\d+\.\s+/)) {
        if (listType !== 'ol') {
          flushList();
          listType = 'ol';
        }
        currentList.push(line.replace(/^[\s]*\d+\.\s+/, ''));
        return;
      }

      // Blockquote
      if (line.startsWith('> ')) {
        flushList();
        elements.push(
          <blockquote key={index} className="border-l-4 border-gray-300 pl-3 my-2 italic text-gray-700">
            {line.substring(2)}
          </blockquote>
        );
        return;
      }

      // Horizontal rule
      if (line.match(/^[-*_]{3,}$/)) {
        flushList();
        elements.push(<hr key={index} className="my-3 border-gray-300" />);
        return;
      }

      // Empty line
      if (line.trim() === '') {
        flushList();
        return;
      }

      // Regular paragraph
      flushList();
      elements.push(
        <p
          key={index}
          className="text-sm my-1"
          dangerouslySetInnerHTML={{ __html: processInlineMarkdown(line) }}
        />
      );
    });

    // Flush any remaining lists or code blocks
    flushList();
    flushCodeBlock();

    return elements;
  };

  const processInlineMarkdown = (text: string): string => {
    let processed = text;

    // Inline code
    processed = processed.replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">$1</code>');

    // Bold
    processed = processed.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold">$1</strong>');
    processed = processed.replace(/__([^_]+)__/g, '<strong class="font-semibold">$1</strong>');

    // Italic
    processed = processed.replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>');
    processed = processed.replace(/_([^_]+)_/g, '<em class="italic">$1</em>');

    // Strikethrough
    processed = processed.replace(/~~([^~]+)~~/g, '<del class="line-through">$1</del>');

    // Links
    processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">$1</a>');

    return processed;
  };

  return <div className={`markdown-content ${className}`}>{renderMarkdown(content)}</div>;
}
