import React, { useState, useEffect } from 'react';

/**
 * MessageContent component that handles showing/hiding thinking process in debate messages
 * and improves text formatting
 */
const MessageContent = ({ content }) => {
  const [showThinking, setShowThinking] = useState(false);
  const [hasThinking, setHasThinking] = useState(false);
  const [processedContent, setProcessedContent] = useState('');
  
  // Process the content to detect and handle thinking sections and improve formatting
  useEffect(() => {
    if (!content) {
      setProcessedContent('');
      return;
    }
    
    // Check if the content contains thinking tags
    const thinkingPattern = /<think>([\s\S]*?)<\/think>/g;
    const hasThinkingTags = thinkingPattern.test(content);
    setHasThinking(hasThinkingTags);
    
    // Reset the pattern (since the test method advances the regex)
    thinkingPattern.lastIndex = 0;
    
    // First, handle thinking sections
    let formattedContent = showThinking ? 
      content.replace(/<think>([\s\S]*?)<\/think>/g, '<div class="thinking-section">$1</div>') :
      content.replace(/<think>[\s\S]*?<\/think>/g, '');
    
    // Then apply additional formatting:
    
    // 1. Format numbered points and lists
    formattedContent = formattedContent
      // Convert numbered points pattern like "1." or "1)" at beginning of line
      .replace(/^\s*(\d+[\.\)])\s+(.+)$/gm, '<div class="numbered-point">$1 $2</div>')
      // Convert bullet points
      .replace(/^\s*[-•]\s+(.+)$/gm, '<div class="bullet-point">• $1</div>');
    
    // 2. Format bold text (both * and _ variants)
    formattedContent = formattedContent
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/_(.*?)_/g, '<em>$1</em>');
    
    // 3. Format quotes
    formattedContent = formattedContent
      .replace(/^\s*>(.+)$/gm, '<blockquote>$1</blockquote>');
    
    // 4. Add paragraph breaks for empty lines
    formattedContent = formattedContent
      .replace(/\n\s*\n/g, '</p><p>');
    
    // 5. Wrap in paragraph tags if not already wrapped 
    if (!formattedContent.startsWith('<p>')) {
      formattedContent = '<p>' + formattedContent + '</p>';
    }
    
    // 6. Make separate points clearer
    formattedContent = formattedContent
      .replace(/(\*simulat(e|ing|es)\*)/g, '<span class="highlight">$1</span>')
      .replace(/(\*enhanc(e|ing|es)\*)/g, '<span class="highlight-positive">$1</span>');
    
    setProcessedContent(formattedContent);
  }, [content, showThinking]);
  
  return (
    <div className="message-content-container">
      <div 
        className="message-content"
        dangerouslySetInnerHTML={{ __html: processedContent }}
      />
      
      {hasThinking && (
        <button 
          className="thinking-toggle"
          onClick={() => setShowThinking(!showThinking)}
        >
          {showThinking ? 'Hide Thinking' : 'Show Thinking'}
        </button>
      )}
    </div>
  );
};

export default MessageContent;