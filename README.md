# 🛍️ Multi Agent Ai Shopping Assistant

An AI-powered shopping assistant application that helps users recognize products from images, ask questions about those products, retrieve purchase links, and fetch relevant information from Wikipedia. The app is available in two modes: a manual app interface and a fully automated multi-agentic chatbot system.

## 🧠 Key Features

### 1. 🖼️ Product Recognition from Images
- Upload an image of a product
- The system uses computer vision and multimodal AI to identify the product name and details

### 2. ❓ Product Q&A
- Ask questions about the product
- The chatbot or app uses LLMs to answer your doubts in natural language

### 3. 🔗 Shopping Link Finder
- Automatically fetches direct shopping links from platforms like Amazon, Flipkart, etc.
- Helps you compare and buy products easily

### 4. 🌐 Wikipedia Info Retrieval
- Fetches general and encyclopedic knowledge about the product from Wikipedia
- Helpful for background or historical information
## 🧠 Technologies and Frameworks Used
   - Langgraph
   - Langchain
   - Generative Ai
   - LLMs

## 🤖 Components

### Manual App
- Run using `new.py`, `streamlit.py`, or `temp.py`
- Users manually interact with the UI to perform tasks

### Multi-Agentic Chatbot
- Located in the `Agentic/` folder
- Automates all features through agents (LLMs, toolchains)
- Coordinates vision, search, and NLP agents to answer queries end-to-end
- Key files:
  - `chatbot.py`: Main bot logic
  - `driver.py`: Task flow driver
  - `edges.py` & `states.py`: Define agent transitions and states
  - `prompts.py`: Houses prompt templates for agents

## Multi-Agentic Architechture
![Architechture](Media%2FAgentic.png)

## Process Flow
![Process Flow](Media%2Fprocess.jpg)

## 🛠️ Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Kushaagra-exe/MultiAgent-ShoppeeAssistant.git
   cd kushaagra-exe-multiagent-shoppeeassistant
   ```

2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the manual app:
   ```bash
   streamlit run new.py
   ```

4. Run Only the agentic chatbot:
   ```bash
   streamlit run Agentic/app.py
   ```

⚠️ Note: Make sure to set up API keys for image recognition, shopping APIs, and language models in a .env File.

## 📓 Notebooks

Explore the `notebooks/` directory to see experiments, tests, and results related to various components like:
* Agentic testing
* Tavily integration
* Chatbot Integration

## 📌 Future Enhancements

* Add multilingual support
* Expand product sources beyond major e-commerce platforms
* Voice-based query support
* Memory-enhanced personalized assistant

## 🙋‍♂️ Author

**Kushaagra Mehta**  
Connect with me on [LinkedIn](https://linkedin.com/in/kushaagraMehta) | [GitHub](https://github.com/kushaagraExe)

<!-- ## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. -->

## Usage Examples
### Manual App
![App Video](Media%2Fapp.gif)

### MultiAgentic Chatbot
![Chatbot Video](Media%2Fchatbot.gif)
