import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './DebateArena.css';

const DebateArena = () => {
  const [debateStatus, setDebateStatus] = useState({
    current_debate: null,
    debate_log: [],
    is_running: false
  });
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch initial debate status
  useEffect(() => {
    fetchDebateStatus();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [debateStatus.debate_log]);

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
    } catch (error) {
      console.error('Error starting new debate:', error);
    } finally {
      setLoading(false);
    }
  };

  // Progress the debate
  const progressDebate = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/debate/progress');
      setDebateStatus(response.data);
    } catch (error) {
      console.error('Error progressing debate:', error);
    } finally {
      setLoading(false);
    }
  };

  // Toggle debate running state
  const toggleDebateRunning = async () => {
    try {
      const response = await axios.post('/api/debate/toggle');
      setDebateStatus(response.data);
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

  // Get debater by position
  const getDebaterByPosition = (position) => {
    if (!debateStatus.current_debate) return null;
    return debateStatus.current_debate.debaters.find(d => d.position === position);
  };

  // Filter messages by debater position
  const getMessagesByPosition = (position) => {
    return debateStatus.debate_log.filter(msg => 
      msg.type === 'debater' && 
      msg.position === position
    );
  };

  // Render system messages
  const renderSystemMessages = () => {
    return debateStatus.debate_log
      .filter(msg => msg.type === 'system')
      .map((msg, index) => (
        <div key={index} className="system-message">
          <div className="system-content">{msg.content}</div>
        </div>
      ));
  };

  // Render debate information
  const renderDebateInfo = () => {
    if (!debateStatus.current_debate) {
      return <div className="no-debate">No active debate. Start a new one!</div>;
    }

    const { topic, round, exchange, finished } = debateStatus.current_debate;
    const proDebater = getDebaterByPosition('pro');
    const antiDebater = getDebaterByPosition('anti');

    return (
      <div className="debate-info">
        <h2 className="debate-topic">{topic}</h2>
        <div className="debate-meta">
          <div className="debate-status">
            {finished ? 'Debate Completed' : `Round ${round}, Exchange ${exchange}`}
          </div>
          <div className="debater-info">
            <div className="pro-debater">
              <div className="debater-name">{proDebater?.codename}</div>
              <div className="debater-model">{proDebater?.name}</div>
            </div>
            <div className="versus">VS</div>
            <div className="anti-debater">
              <div className="debater-name">{antiDebater?.codename}</div>
              <div className="debater-model">{antiDebater?.name}</div>
            </div>
          </div>
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
            className="start-button"
          >
            New Debate
          </button>
          {debateStatus.current_debate && !debateStatus.current_debate.finished && (
            <>
              <button 
                onClick={progressDebate} 
                disabled={loading || !debateStatus.is_running}
                className="progress-button"
              >
                Next Step
              </button>
              <button 
                onClick={toggleDebateRunning}
                disabled={loading}
                className={`toggle-button ${debateStatus.is_running ? 'pause' : 'resume'}`}
              >
                {debateStatus.is_running ? 'Pause' : 'Resume'}
              </button>
            </>
          )}
          {debateStatus.debate_log.length > 0 && (
            <div className="export-buttons">
              <button onClick={() => exportDebate('markdown')} className="export-button">
                Export (MD)
              </button>
              <button onClick={() => exportDebate('text')} className="export-button">
                Export (TXT)
              </button>
            </div>
          )}
        </div>
      </div>

      {renderDebateInfo()}

      <div className="system-messages">
        {renderSystemMessages()}
      </div>

      <div className="debate-container">
        <div className="pro-column">
          <div className="column-header">PRO</div>
          <div className="messages-container">
            {getMessagesByPosition('pro').map((msg, index) => (
              <div key={index} className="message pro-message">
                <div className="message-header">
                  <span className="debater-name">{msg.debater}</span>
                  <span className="model-name">({msg.model})</span>
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="anti-column">
          <div className="column-header">ANTI</div>
          <div className="messages-container">
            {getMessagesByPosition('anti').map((msg, index) => (
              <div key={index} className="message anti-message">
                <div className="message-header">
                  <span className="debater-name">{msg.debater}</span>
                  <span className="model-name">({msg.model})</span>
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div ref={messagesEndRef} />
    </div>
  );
};

export default DebateArena;