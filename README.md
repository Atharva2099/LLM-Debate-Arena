# LLM Debate Arena

> *Where AI models battle it out in the marketplace of ideas*

## What is this? 

The LLM Debate Arena is a full-stack web application that lets you host and watch debates between different language models. It pits models against each other to argue opposing sides of various topics, from philosophical questions to absurdist propositions.

![LLM Debate Arena Screenshot](https://via.placeholder.com/800x450)

## Why Though?

Ever wonder how different LLMs would argue against each other? This project lets you find out! I created this as a fun side project to:

1. Observe how different medium-sized models (8-20B parameters) reason through arguments
2. Establish a baseline for future benchmarking work on LLM debate capabilities
3. Create a foundation for more sophisticated LLM-as-Judge evaluation frameworks
4. Have some fun watching AI models try to convince each other (and fail spectacularly)

## Features

- **Auto-Generated Debates**: One-click to start a debate with randomly selected topics and models
- **Position Switching**: Models switch positions between rounds for fairness
- **Multiple Model Support**: Currently supports Phi-4, Gemini 2.5 Flash, and Qwen 14B
- **Real-Time Progress**: Watch the debate unfold exchange by exchange
- **Auto-Progress**: Set it to auto and watch the debate run by itself
- **Debate Export**: Save debates in Markdown or text format for sharing or analysis
- **Responsive UI**: Clean, modern interface that adapts to various screen sizes

## Tech Stack

### Backend (Python)
- Flask REST API
- OpenRouter API integration for multi-model access
- Structured debate management system

### Frontend (React)
- Modern React with hooks
- Clean, responsive design with CSS
- Real-time updates and auto-scrolling

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- OpenRouter API key (sign up at [openrouter.ai](https://openrouter.ai))

### Installation

1. Clone this repo
```bash
git clone https://github.com/yourusername/llm-debate-arena.git
cd llm-debate-arena
```

2. Set up the backend
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file in the backend directory
echo "OPENROUTER_API_KEY=your_api_key_here" > backend/.env
```

3. Set up the frontend
```bash
cd frontend
npm install
```

4. Start the servers
```bash
# Start the backend (from the root directory)
cd backend
python app.py

# Start the frontend (in another terminal)
cd frontend
npm start
```

5. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Click "New Debate" to start a fresh debate
2. Watch as the models exchange arguments
3. Use "Auto-Progress" to let the debate run automatically
4. Export the debate when it's complete

## Supported Models

The project currently supports these models through OpenRouter:
- Microsoft Phi-4
- Google Gemini 2.5 Flash
- Qwen 14B

## Future Plans 

This project serves as a foundation for a more comprehensive LLM benchmarking framework. Future plans include:

- **LLM-as-Judge**: Implementing a judging system where another model evaluates debate quality
- **More Debate Formats**: Adding different debate styles beyond basic pro/con exchanges
- **Custom Topics**: Allowing users to specify debate topics
- **Better Evaluation Metrics**: Developing objective measures for argument quality and reasoning
- **More Models**: Expanding the range of supported models for broader comparisons


## License

MIT

## Acknowledgements

- This project uses OpenRouter to access various models
- Built with React and Flask
- Inspired by human debate competitions and the need for better LLM evaluation methods