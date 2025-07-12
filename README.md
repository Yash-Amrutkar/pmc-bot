# PMC (Prime Minister's Office) AI Chatbot

An intelligent AI chatbot designed to provide information and assistance related to the Prime Minister's Office (PMO) website content.

## Features

- **Web Scraping**: Automatically extracts content from PMC website
- **Vector Database**: Stores and retrieves relevant information efficiently
- **AI-Powered Responses**: Uses OpenAI's GPT models for intelligent responses
- **Web Interface**: Beautiful Streamlit-based chat interface
- **Real-time Chat**: Interactive conversation experience
- **Context Awareness**: Maintains conversation context

## Project Structure

```
pmc-bot/
├── data/                   # Scraped website data
├── models/                 # AI models and embeddings
├── src/                    # Source code
│   ├── scraper.py         # Website scraper
│   ├── chatbot.py         # Main chatbot logic
│   ├── vector_store.py    # Vector database operations
│   └── utils.py           # Utility functions
├── web_app/               # Web interface
│   └── app.py            # Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key
4. Run the scraper to collect data:
   ```bash
   python src/scraper.py
   ```
5. Start the web application:
   ```bash
   streamlit run web_app/app.py
   ```

## Usage

1. Open your browser and go to `http://localhost:8501`
2. Start chatting with the PMC chatbot
3. Ask questions about PMO policies, announcements, or general information

## Technologies Used

- **Python**: Core programming language
- **OpenAI GPT**: AI language model for responses
- **LangChain**: Framework for building AI applications
- **ChromaDB**: Vector database for similarity search
- **Streamlit**: Web interface framework
- **BeautifulSoup**: Web scraping
- **Sentence Transformers**: Text embeddings

## API Endpoints

- `GET /`: Main chat interface
- `POST /chat`: Process chat messages
- `GET /health`: Health check endpoint

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL_NAME`: GPT model to use (default: gpt-3.5-turbo)
- `TEMPERATURE`: Response creativity (0.0-1.0)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes. 
