# AI Agent Integration Project

## Description
This project implements an AI Agent Integration system using Python. The system features intelligent agents with memory management capabilities, allowing them to handle multi-turn conversations, store and retrieve past interactions, and integrate with various tools and APIs.

## Features
- AI Agent with contextual memory using SQLite
- Modular architecture for scalability and maintenance
- Command-line interface for user interactions
- Comprehensive logging and error handling
- Unit and integration tests for reliability

## Setup Instructions
1. **Clone the Repository:**
    git clone https://github.com/dadudekc/ai_agent_project.git
    cd ai_agent_project
2. **Install Dependencies:**
    pip install -r requirements.txt
3. **Run the AI Agent:**
    pip install -r requirements.txt

**Usage**
Interact with the AI agent through the command-line interface. Type your messages, and the AI will respond accordingly. Type exit or quit to end the conversation.

**Testing**
Run unit tests using:
    python -m unittest discover tests

Contributing
Contributions are welcome! Please open issues and submit pull requests for any enhancements or bug fixes.

License
This project is licensed under the MIT License.


---

### **2. requirements.txt**

```plaintext
# requirements.txt

# SQLite is included with Python, but if using PostgreSQL, include psycopg2
psycopg2-binary>=2.9.6
