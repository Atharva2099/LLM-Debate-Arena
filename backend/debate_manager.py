"""
LLM Debate Arena - Debate Manager
This module handles the core logic for managing debates between language models
"""

import random
import json
import time
from typing import List, Dict, Tuple, Optional, Any

# Constants
MODELS = [
    {"id": "phi4", "name": "Phi-4", "api_endpoint": "/api/generate/phi4"},
    {"id": "gemini", "name": "Gemini 2.5 Flash", "api_endpoint": "/api/generate/gemini"},
    {"id": "qwen", "name": "Qwen 14B", "api_endpoint": "/api/generate/qwen"}
]

SERIOUS_TOPICS = [
    "Why humans are precious in a Post-AI world",
    "Universal basic income should be implemented globally",
    "Digital privacy should be considered a fundamental human right",
    "Space colonization should be prioritized over solving Earth's problems",
    "Algorithmic decision-making creates more fairness than human judgment",
    "Genetic engineering of humans should be strictly regulated",
    "Decentralized governance models are superior to traditional hierarchies",
    "The metaverse will fundamentally improve human connection"
]

NON_CONVENTIONAL_TOPICS = [
    "Why you should never name your child James",
    "Why elephants should actually weigh exactly 62.34 pounds",
    "What if humans worked exclusively at night and slept during the day",
    "Breakfast cereal should be eaten with orange juice instead of milk",
    "All doors should open outward instead of inward",
    "Socks should be sold individually rather than in pairs",
    "Keyboards should be arranged in alphabetical order rather than QWERTY",
    "Clouds should be rectangular instead of their current shapes",
    "Wednesday should be removed from the calendar entirely",
    "People should communicate exclusively through interpretive dance on Tuesdays"
]

DEBATER_CODENAMES = [
    "Debater Alpha", "Debater Beta", "Debater Gamma", "Debater Delta", 
    "Debater Epsilon", "Debater Zeta", "Debater Eta", "Debater Theta",
    "Debater Iota", "Debater Kappa", "Debater Lambda", "Debater Mu",
    "Debater Nu", "Debater Xi", "Debater Omicron", "Debater Pi",
    "Debater Rho", "Debater Sigma", "Debater Tau", "Debater Upsilon",
    "Debater Phi", "Debater Chi", "Debater Psi", "Debater Omega"
]

DEBATE_CONSTANTS = {
    "EXCHANGES_PER_ROUND": 10,
    "ROUNDS_PER_DEBATE": 2,
    "REGULAR_WORD_LIMIT": 150,
    "CONCLUSION_WORD_LIMIT": 200,
    "TEMPERATURE": 0.7
}

PROMPT_TEMPLATES = {
    "OPENING_STATEMENT": 
        """You are participating in a structured debate on the topic: '{topic}'. 
        You have been assigned the {position} position. 
        Make your opening argument in {word_limit} words or less. 
        Focus on making a compelling, logical case supported by evidence where appropriate.
        Identify yourself as {codename}.""",
    
    "REGULAR_EXCHANGE": 
        """You are participating in a structured debate on the topic: '{topic}'. 
        You have been assigned the {position} position.
        Your opponent, {opponent_codename}, just made the following argument:
        
        "{opponent_argument}"
        
        Respond to their argument in {word_limit} words or less.
        Make your argument compelling and logical, addressing their points directly.
        Identify yourself as {codename}.""",
    
    "CONCLUSION_STATEMENT":
        """You are participating in a structured debate on the topic: '{topic}'. 
        You have been assigned the {position} position.
        This is your concluding statement. Summarize your main arguments and address the
        key points from your opponent's position in {word_limit} words or less.
        Make your final case compelling and memorable.
        Identify yourself as {codename}."""
}


class DebateManager:
    """Manager class for handling LLM debates"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize the debate manager
        
        Args:
            api_keys: Dictionary of API keys for each model
        """
        self.api_keys = api_keys or {}
        self.current_debate = None
        self.debate_log = []
        self.is_running = False
    
    def start_new_debate(self) -> Dict[str, Any]:
        """
        Initialize a new debate with random topic and participants
        
        Returns:
            Dict containing the debate setup information
        """
        # Select a random topic pool and topic
        topic_pool = random.choice([SERIOUS_TOPICS, NON_CONVENTIONAL_TOPICS])
        topic = random.choice(topic_pool)
        
        # Select two random models
        selected_models = random.sample(MODELS, 2)
        
        # Assign random codenames
        selected_codenames = random.sample(DEBATER_CODENAMES, 2)
        
        # Create debate structure
        self.current_debate = {
            "topic": topic,
            "round": 1,
            "exchange": 0,
            "debaters": [
                {
                    **selected_models[0],
                    "position": "pro",
                    "codename": selected_codenames[0]
                },
                {
                    **selected_models[1],
                    "position": "anti",
                    "codename": selected_codenames[1]
                }
            ],
            "current_speaker": 0,  # Index of the debater speaking next
            "finished": False,
            "timestamp": time.time()
        }
        
        # Add the initial system message to the log
        self.debate_log = [{
            "type": "system",
            "content": f"SLM Debate Tournament: New Debate Started\n\nTopic: \"{topic}\"\n\n"
                      f"{selected_codenames[0]} ({selected_models[0]['name']}) will argue FOR the proposition.\n"
                      f"{selected_codenames[1]} ({selected_models[1]['name']}) will argue AGAINST the proposition.\n\n"
                      f"Round 1 begins now.",
            "timestamp": time.time()
        }]
        
        self.is_running = True
        return self.get_debate_status()
    
    def progress_debate(self) -> Dict[str, Any]:
        """
        Progress the debate to the next step
        
        Returns:
            Dict containing the updated debate status
        """
        if not self.current_debate or not self.is_running or self.current_debate["finished"]:
            return self.get_debate_status()
        
        debate = self.current_debate
        speaker = debate["debaters"][debate["current_speaker"]]
        
        # Determine what happens next
        if debate["round"] in [1, 2]:
            if debate["exchange"] < DEBATE_CONSTANTS["EXCHANGES_PER_ROUND"]:
                # Regular exchange
                message_type = "opening" if debate["exchange"] == 0 else "regular"
                word_limit = (DEBATE_CONSTANTS["CONCLUSION_WORD_LIMIT"] 
                             if debate["exchange"] == DEBATE_CONSTANTS["EXCHANGES_PER_ROUND"] - 1 
                             else DEBATE_CONSTANTS["REGULAR_WORD_LIMIT"])
                
                # Here we would normally make an API call to the LLM
                # For now, we'll just add a placeholder message
                new_message = {
                    "type": "debater",
                    "debater": speaker["codename"],
                    "model": speaker["name"],
                    "content": f"[This is where {speaker['name']} ({speaker['codename']}) would provide a {word_limit}-word "
                              f"{speaker['position']} {message_type} for the topic \"{debate['topic']}\"]",
                    "position": speaker["position"],
                    "exchange": debate["exchange"],
                    "timestamp": time.time()
                }
                
                self.debate_log.append(new_message)
                
                # Switch to the other speaker
                debate["current_speaker"] = 1 if debate["current_speaker"] == 0 else 0
                
                # If both speakers have spoken, increment the exchange counter
                if debate["current_speaker"] == 0:
                    debate["exchange"] += 1
            else:
                # End of round
                if debate["round"] == 1:
                    # Switch positions for round 2
                    for debater in debate["debaters"]:
                        debater["position"] = "anti" if debater["position"] == "pro" else "pro"
                    
                    # Reset for round 2
                    debate["round"] = 2
                    debate["exchange"] = 0
                    
                    # Add round transition message
                    self.debate_log.append({
                        "type": "system",
                        "content": f"Round 1 Complete\n\nPositions will now be switched for Round 2.\n\n"
                                  f"{debate['debaters'][0]['codename']} will now argue "
                                  f"{'FOR' if debate['debaters'][0]['position'] == 'pro' else 'AGAINST'} the proposition.\n"
                                  f"{debate['debaters'][1]['codename']} will now argue "
                                  f"{'FOR' if debate['debaters'][1]['position'] == 'pro' else 'AGAINST'} the proposition.\n\n"
                                  f"Round 2 begins now.",
                        "timestamp": time.time()
                    })
                else:
                    # End of debate
                    debate["finished"] = True
                    
                    # Add debate conclusion message
                    self.debate_log.append({
                        "type": "system",
                        "content": f"Debate Concluded\n\nBoth rounds completed for the topic: \"{debate['topic']}\"\n\n"
                                  f"In Round 1:\n"
                                  f"- {debate['debaters'][0]['codename']} ({debate['debaters'][0]['name']}) argued "
                                  f"{'AGAINST' if debate['debaters'][0]['position'] == 'pro' else 'FOR'}\n"
                                  f"- {debate['debaters'][1]['codename']} ({debate['debaters'][1]['name']}) argued "
                                  f"{'AGAINST' if debate['debaters'][1]['position'] == 'pro' else 'FOR'}\n\n"
                                  f"In Round 2:\n"
                                  f"- {debate['debaters'][0]['codename']} ({debate['debaters'][0]['name']}) argued "
                                  f"{'FOR' if debate['debaters'][0]['position'] == 'pro' else 'AGAINST'}\n"
                                  f"- {debate['debaters'][1]['codename']} ({debate['debaters'][1]['name']}) argued "
                                  f"{'FOR' if debate['debaters'][1]['position'] == 'pro' else 'AGAINST'}\n\n"
                                  f"You can now manually provide this debate log to a judge model.",
                        "timestamp": time.time()
                    })
                    
                    self.is_running = False
        
        return self.get_debate_status()
    
    def toggle_debate_running(self) -> Dict[str, Any]:
        """
        Toggle the running state of the current debate
        
        Returns:
            Dict containing the updated debate status
        """
        if self.current_debate and not self.current_debate["finished"]:
            self.is_running = not self.is_running
        return self.get_debate_status()
    
    def get_debate_status(self) -> Dict[str, Any]:
        """
        Get the current status of the debate
        
        Returns:
            Dict containing the current debate status
        """
        return {
            "current_debate": self.current_debate,
            "debate_log": self.debate_log,
            "is_running": self.is_running
        }
    
    def export_debate(self, format_type: str = "markdown") -> str:
        """
        Export the debate log in the specified format
        
        Args:
            format_type: Either "markdown" or "text"
            
        Returns:
            String containing the formatted debate log
        """
        if not self.debate_log:
            return "No debate to export."
        
        if format_type == "markdown":
            return self._export_to_markdown()
        else:
            return self._export_to_text()
    
    def _export_to_markdown(self) -> str:
        """
        Export the debate log to Markdown format
        
        Returns:
            String containing the Markdown formatted debate log
        """
        markdown = "# SLM Debate Tournament Log\n\n"
        
        for msg in self.debate_log:
            if msg["type"] == "system":
                markdown += f"## {msg['content']}\n\n"
            elif msg["type"] == "debater":
                markdown += f"### {msg['debater']} ({msg['position'].upper()})\n\n{msg['content']}\n\n"
        
        return markdown
    
    def _export_to_text(self) -> str:
        """
        Export the debate log to plain text format
        
        Returns:
            String containing the text formatted debate log
        """
        text = "SLM Debate Tournament Log\n\n"
        
        for msg in self.debate_log:
            if msg["type"] == "system":
                text += f"{msg['content']}\n\n"
            elif msg["type"] == "debater":
                text += f"{msg['debater']} ({msg['position'].upper()}):\n{msg['content']}\n\n"
        
        return text
    
    def update_api_keys(self, api_keys: Dict[str, str]) -> None:
        """
        Update the API keys
        
        Args:
            api_keys: Dictionary of API keys for each model
        """
        self.api_keys = api_keys


# Function to create a properly formatted API call to the LLM
def generate_llm_prompt(debate_data: Dict[str, Any], model_id: str, 
                       position: str, exchange: int, opponent_message: Optional[str] = None) -> str:
    """
    Generate a prompt for the LLM based on the current debate state
    
    Args:
        debate_data: Current debate data
        model_id: ID of the model to generate for
        position: Position ("pro" or "anti")
        exchange: Current exchange number
        opponent_message: The opponent's last message content
        
    Returns:
        Formatted prompt string for the LLM
    """
    topic = debate_data["topic"]
    
    # Find the debater with this model_id
    debater = None
    opponent = None
    for d in debate_data["debaters"]:
        if d["id"] == model_id:
            debater = d
        else:
            opponent = d
    
    if not debater or not opponent:
        raise ValueError(f"Could not find debater with model_id {model_id}")
    
    word_limit = (DEBATE_CONSTANTS["CONCLUSION_WORD_LIMIT"] 
                 if exchange == DEBATE_CONSTANTS["EXCHANGES_PER_ROUND"] - 1 
                 else DEBATE_CONSTANTS["REGULAR_WORD_LIMIT"])
    
    # Determine which prompt template to use
    if exchange == 0:
        # Opening statement
        template = PROMPT_TEMPLATES["OPENING_STATEMENT"]
        prompt = template.format(
            topic=topic,
            position=position,
            word_limit=word_limit,
            codename=debater["codename"]
        )
    elif exchange == DEBATE_CONSTANTS["EXCHANGES_PER_ROUND"] - 1:
        # Conclusion statement
        template = PROMPT_TEMPLATES["CONCLUSION_STATEMENT"]
        prompt = template.format(
            topic=topic,
            position=position,
            word_limit=word_limit,
            codename=debater["codename"]
        )
    else:
        # Regular exchange
        template = PROMPT_TEMPLATES["REGULAR_EXCHANGE"]
        prompt = template.format(
            topic=topic,
            position=position,
            opponent_codename=opponent["codename"],
            opponent_argument=opponent_message,
            word_limit=word_limit,
            codename=debater["codename"]
        )
    
    return prompt


# Example usage
if __name__ == "__main__":
    # Create a debate manager
    manager = DebateManager()
    
    # Start a new debate
    debate_status = manager.start_new_debate()
    print(f"Started new debate on topic: {debate_status['current_debate']['topic']}")
    
    # Progress the debate a few steps
    for _ in range(5):
        debate_status = manager.progress_debate()
        latest_message = debate_status['debate_log'][-1]
        print(f"[{latest_message['type']}] {latest_message.get('debater', 'System')}: {latest_message['content'][:50]}...")
        time.sleep(1)
    
    # Export the debate to markdown
    markdown_export = manager.export_debate(format_type="markdown")
    print("\nMarkdown Export Example (truncated):")
    print(markdown_export[:200] + "...")