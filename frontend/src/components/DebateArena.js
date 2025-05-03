import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './DebateArena.css';
import MessageContent from './MessageContent';
import ModelDisplay from './ModelDisplay';

const DebateArena = () => {
  const [debateStatus, setDebateStatus] = useState({
    current_debate: null,
    debate_log: [],
    is_running: false
  });
  const [loading, setLoading] = useState(false);
  const [autoProgress, setAutoProgress] = useState(false);
  const [progressTimer, setProgressTimer] = useState(null);
  const messagesEndRef = useRef(null);

  // Fetch initial debate status
  useEffect(() => {
    fetchDebateStatus();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [debateStatus.debate_log]);
  
  // Clean up any timers when component unmounts
  useEffect(() => {
    return () => {
      if (progressTimer) {
        clearTimeout(progressTimer);
      }
    };
  }, [progressTimer]);
  
  // Handle auto-progression for debates
  useEffect(() => {
    if (autoProgress && 
        debateStatus.is_running && 
        debateStatus.current_debate && 
        !debateStatus.current_debate.finished) {
      const timer = setTimeout(() => {
        progressDebate();
      }, 1000); // Wait 1 second before next progression
      
      setProgressTimer(timer);
      return () => clearTimeout(timer);
    }
  }, [autoProgress, debateStatus, debateStatus.debate_log.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Fetch current debate status
  const fetchDebateStatus = async () => {
    try {
      const response = await axios.get('/api/debate/status');
      setDebateStatus(response.data);
    } catch (error) {
      console.error('Error fetching debate status:', error);
    }
  };

  // Start a new debate
  const startNewDebate = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/debate/start');
      setDebateStatus(response.data);
      // Automatically start progression when a new debate is created
      setAutoProgress(true);
    } catch (error) {
      console.error('Error starting new debate:', error);
    } finally {
      setLoading(false);
    }
  };

  // Progress the debate
  const progressDebate = async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      const response = await axios.post('/api/debate/progress');
      setDebateStatus(response.data);
      
      // Check if we've reached the end of a round but not the end of the debate
      const debate = response.data.current_debate;
      if (debate && 
          !debate.finished && 
          debate.exchange === 0 && 
          debate.round === 2) {
        // We've reached the start of round 2, pause auto-progression
        setAutoProgress(false);
      }
    } catch (error) {
      console.error('Error progressing debate:', error);
      // If there's an error, stop auto-progression
      setAutoProgress(false);
    } finally {
      setLoading(false);
    }
  };

  // Toggle auto-progression
  const toggleAutoProgress = () => {
    const newState = !autoProgress;
    setAutoProgress(newState);
  };

  // Toggle debate running state
  const toggleDebateRunning = async () => {
    try {
      const response = await axios.post('/api/debate/toggle');
      setDebateStatus(response.data);
      
      // If debate is no longer running, also stop auto-progression
      if (!response.data.is_running) {
        setAutoProgress(false);
      }
    } catch (error) {
      console.error('Error toggling debate state:', error);
    }
  };

  // Export debate
  const exportDebate = async (format = 'markdown') => {
    try {
      const response = await axios.get(`/api/debate/export?format=${format}`);
      // Create a blob and download it
      const blob = new Blob([response.data.log], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `debate-export-${new Date().toISOString().slice(0, 10)}.${format === 'markdown' ? 'md' : 'txt'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting debate:', error);
    }
  };

  // Render debate information
  const renderDebateInfo = () => {
    if (!debateStatus.current_debate) {
      return <div className="no-debate">No active debate. Start a new one!</div>;
    }

    const { topic, round, exchange, finished } = debateStatus.current_debate;
    
    return (
      <div className="debate-info">
        <h2 className="debate-topic">{topic}</h2>
        <div className="debate-meta">
          <div className="debate-status">
            {finished ? 'Debate Completed' : `Round ${round}, Exchange ${exchange}`}
          </div>
          <div className="debater-info">
            {debateStatus.current_debate.debaters.map((debater, index) => (
              <span key={index} className={`debater-badge ${debater.position}`}>
                {index > 0 && " vs "}
                {debater.codename} ({debater.name})
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Render chat messages
  const renderChatMessages = () => {
    if (!debateStatus.debate_log.length) {
      return null;
    }

    // Group messages by round and exchange for better visualization
    const messageGroups = [];
    let currentRound = 1;
    let currentExchange = -1;

    debateStatus.debate_log.forEach((msg) => {
      if (msg.type === 'system') {
        messageGroups.push({
          type: 'system',
          content: msg.content,
          timestamp: msg.timestamp
        });
      } else if (msg.type === 'debater') {
        // Check if this is a new exchange
        if (msg.exchange !== currentExchange || msg.round !== currentRound) {
          currentExchange = msg.exchange;
          
          // Add conclusion marker if it's the last exchange
          if (debateStatus.current_debate && 
              currentExchange === debateStatus.current_debate.total_exchanges - 1) {
            messageGroups.push({
              type: 'stage',
              content: 'Conclusion Statements'
            });
          }
        }

        messageGroups.push({
          type: 'message',
          position: msg.position,
          debater: msg.debater,
          model: msg.model,
          content: msg.content,
          timestamp: msg.timestamp,
          exchange: msg.exchange
        });
      }
    });

    return messageGroups.map((group, index) => {
      if (group.type === 'system') {
        return (
          <div key={index} className="system-message">
            {group.content}
          </div>
        );
      } else if (group.type === 'stage') {
        return (
          <div key={index} className="debate-stage">
            {group.content}
          </div>
        );
      } else {
        // Regular message
        const isProPosition = group.position === 'pro';
        return (
          <div 
            key={index} 
            className={`message ${isProPosition ? 'pro-message' : 'anti-message'}`}
          >
            <div className="message-header">
              <div className="debater-info-container">
                <span className="debater-name">{group.debater}</span>
                <span className={`position-badge ${isProPosition ? 'pro-badge' : 'anti-badge'}`}>
                  {isProPosition ? 'PRO' : 'ANTI'}
                </span>
              </div>
              <ModelDisplay model={group.model} position={group.position} />
            </div>
            <MessageContent content={group.content} />
          </div>
        );
      }
    });
  };

  // Render loading indicator during generation
  const renderThinkingIndicator = () => {
    if (!loading || !debateStatus.is_running) return null;
    
    // Determine which model is currently "thinking"
    let currentModel = "AI";
    let currentPosition = "";
    
    if (debateStatus.current_debate) {
      const speaker = debateStatus.current_debate.debaters[debateStatus.current_debate.current_speaker];
      currentModel = speaker.name;
      currentPosition = speaker.position === 'pro' ? 'PRO' : 'ANTI';
    }
    
    return (
      <div className="thinking-indicator">
        <span>{currentModel} ({currentPosition}) is thinking</span>
        <div className="dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    );
  };

  return (
    <div className="debate-arena">
      <div className="debate-header">
        <h1>LLM Debate Arena</h1>
        <div className="control-buttons">
          <button 
            onClick={startNewDebate} 
            disabled={loading || (debateStatus.current_debate && !debateStatus.current_debate.finished)}
            className="button start-button"
          >
            New Debate
          </button>
        </div>
      </div>

      {renderDebateInfo()}
      
      <div className="chat-container">
        {renderChatMessages()}
        {renderThinkingIndicator()}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="debate-footer">
        {debateStatus.current_debate && !debateStatus.current_debate.finished && (
          <>
            {!autoProgress && (
              <button 
                onClick={progressDebate} 
                disabled={loading || !debateStatus.is_running}
                className="button next-button"
              >
                Next Exchange
              </button>
            )}
            <button 
              onClick={toggleAutoProgress}
              disabled={!debateStatus.is_running || loading}
              className={`button ${autoProgress ? 'pause' : 'resume'}`}
            >
              {autoProgress ? 'Pause Auto-Progress' : 'Auto-Progress'}
            </button>
            <button 
              onClick={toggleDebateRunning}
              disabled={loading}
              className={`button toggle-button ${debateStatus.is_running ? 'pause' : 'resume'}`}
            >
              {debateStatus.is_running ? 'Pause Debate' : 'Resume Debate'}
            </button>
          </>
        )}
        {debateStatus.debate_log.length > 0 && (
          <>
            <button onClick={() => exportDebate('markdown')} className="button export-button">
              Export (MD)
            </button>
            <button onClick={() => exportDebate('text')} className="button export-button">
              Export (TXT)
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default DebateArena;