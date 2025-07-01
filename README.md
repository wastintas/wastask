# WasTask - AI-Native Project Management System

WasTask is a revolutionary AI-native project management system built on Google's Agent Development Kit (ADK). It combines multiple specialized AI agents to automate project planning, task management, GitHub integration, and analytics.

## Features

- **Multi-Agent Architecture**: Specialized AI agents for different aspects of project management
- **Intelligent Planning**: Advanced task decomposition and timeline estimation
- **GitHub Integration**: Bidirectional sync with GitHub repositories
- **Cost Optimization**: Smart model routing and semantic caching
- **CLI & Web Interface**: Comprehensive command-line and web interfaces
- **Real-time Analytics**: Project progress tracking and performance insights

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching)
- PostgreSQL (for data persistence)
- API keys for LLM providers (OpenAI, Anthropic, Google)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wastask
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
# Database setup commands will be added
```

### Usage

#### CLI Commands

Create a new project:
```bash
wastask project create --name "My Project" --description "Project description"
```

Create a detailed project plan:
```bash
wastask project plan proj_001 "Build a web application with user authentication"
```

Create tasks:
```bash
wastask task create --project proj_001 --title "Setup database" --priority high
```

Chat with the AI assistant:
```bash
wastask chat "What tasks should I prioritize this week?"
```

List projects:
```bash
wastask project list --status active
```

Analyze project progress:
```bash
wastask analyze --project proj_001
```

#### Interactive Mode

For a more guided experience, use the interactive mode:
```bash
wastask project create --interactive
```

## Architecture

### Core Agents

1. **Coordinator Agent**: Main orchestrator that routes requests to specialized agents
2. **Planning Agent**: Handles project planning, task decomposition, and timeline estimation
3. **Task Agent**: Manages task lifecycle, assignments, and status updates
4. **GitHub Agent**: Integrates with GitHub for issue sync and PR management
5. **Analytics Agent**: Provides insights, reports, and performance analysis

### Technology Stack

- **Framework**: Google ADK for agent orchestration
- **Backend**: FastAPI for REST API
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for semantic caching
- **CLI**: Click with Rich for beautiful terminal interfaces
- **LLM Integration**: LiteLLM for model flexibility

## Configuration

The system can be configured through environment variables or configuration files. Key settings include:

- **Model Selection**: Choose between different LLM models for different complexity levels
- **Cost Management**: Set daily cost limits and enable semantic caching
- **GitHub Integration**: Configure repository access and webhook settings
- **Security**: Authentication, rate limiting, and access control

## Development

### Project Structure

```
wastask/
├── agents/          # AI agents
├── core/           # Core models and utilities
├── api/            # REST API endpoints
├── cli/            # Command-line interface
├── tools/          # Shared tools and functions
├── config/         # Configuration management
└── tests/          # Test suites
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black wastask/

# Lint code
ruff check wastask/

# Type checking
mypy wastask/
```

## API Documentation

When running the server, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Repository Issues](https://github.com/your-org/wastask/issues)
- Documentation: [Full Documentation](https://wastask.readthedocs.io)

## Roadmap

### Phase 1 (Current)
- [x] Core agent architecture
- [x] Basic CLI interface
- [x] Project and task management
- [ ] GitHub integration
- [ ] Web API

### Phase 2 (Next)
- [ ] Advanced analytics
- [ ] Team collaboration features
- [ ] Mobile app
- [ ] Integrations (Slack, Jira, etc.)

### Phase 3 (Future)
- [ ] AI-powered code generation
- [ ] Advanced workflow automation
- [ ] Enterprise features
- [ ] Multi-tenant support