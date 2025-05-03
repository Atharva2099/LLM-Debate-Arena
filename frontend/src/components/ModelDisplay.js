import React from 'react';

/**
 * ModelDisplay component that shows model information in a more visually appealing way
 */
const ModelDisplay = ({ model, position }) => {
  // Map model names to nicer display names and add any model-specific styling
  const getModelInfo = (modelName) => {
    const modelMap = {
      "Phi-4": {
        displayName: "Microsoft Phi-4",
        color: "#00a4ef" // Microsoft blue
      },
      "Gemini 2.5 Flash": {
        displayName: "Gemini 2.5 Flash",
        color: "#4285f4" // Google blue
      },
      "Qwen 14B": {
        displayName: "Qwen 14B",
        color: "#ff6a00" // Alibaba orange
      }
    };
    
    // Default values if model not in our map
    return modelMap[modelName] || {
      displayName: modelName,
      color: position === 'pro' ? '#3d5afe' : '#ff5252'
    };
  };
  
  const modelInfo = getModelInfo(model);
  
  return (
    <div className="model-display">
      <div 
        className="model-icon"
        style={{ backgroundColor: modelInfo.color }}
      ></div>
      <span className="model-name">{modelInfo.displayName}</span>
    </div>
  );
};

export default ModelDisplay;