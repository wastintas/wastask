# WasTask - AI-Powered Project Management

WasTask is an intelligent project management system that transforms Product Requirements Documents (PRDs) into actionable tasks using AI agents.

## 🚀 Features

- **AI-Powered PRD Analysis**: Automatically analyze and enhance PRD quality
- **Intelligent Task Generation**: Generate detailed tasks with effort estimates  
- **Technology Recommendations**: Get tech stack suggestions based on requirements
- **Project Timeline Estimation**: Automatic complexity analysis and timeline prediction
- **Database Integration**: Store and manage projects and tasks
- **Interactive Mode**: Get clarification questions for better analysis

## 📋 Quick Start

### Installation

```bash
# Setup WasTask
python setup.py
```

### Basic Usage

```bash
# Analyze a PRD and generate tasks
python wastask.py prd analyze my_project.md

# Save results to database
python wastask.py prd analyze my_project.md --output db

# List projects
python wastask.py db list

# Show project details
python wastask.py db show 1
```

## 🛠️ CLI Commands

### PRD Analysis
```bash
# Basic analysis
python wastask.py prd analyze <prd_file>

# With options  
python wastask.py prd analyze <prd_file> --verbose --interactive --output json
```

### Database Management
```bash
# Setup database
python wastask.py db setup

# List all projects
python wastask.py db list

# Show project details
python wastask.py db show <project_id>

# Database statistics
python wastask.py db stats
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