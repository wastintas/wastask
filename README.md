# WasTask - AI-Powered Project Management

WasTask is an intelligent project management system that transforms Product Requirements Documents (PRDs) into actionable tasks using AI agents.

## 🚀 Quick Start

```bash
# Setup WasTask (installs dependencies, creates config)
python setup.py

# Analyze a PRD and generate tasks  
uv run python wastask.py prd analyze my_project.md

# Save results to database
uv run python wastask.py prd analyze my_project.md --output db

# View projects and tasks
uv run python wastask.py db list
uv run python wastask.py db show 1
```

## 🎯 Key Features

- **AI-Powered PRD Analysis**: Automatically analyze and enhance PRD quality
- **Intelligent Task Generation**: Generate detailed tasks with effort estimates  
- **Technology Recommendations**: Get tech stack suggestions based on requirements
- **Database Integration**: Store and manage projects with migration system
- **Rich CLI Interface**: Beautiful terminal output with tables and progress

## 📊 What WasTask Does

**Input**: Simple PRD document  
**Output**: Complete project breakdown with:
- 📝 Enhanced PRD (AI-improved)
- 🛠️ Technology recommendations
- 📋 Detailed task list with estimates
- ⏱️ Timeline and complexity analysis
- 🗄️ Everything saved to database

## 🛠️ CLI Commands

```bash
# PRD Analysis
uv run python wastask.py prd analyze <file>               # Analyze PRD
uv run python wastask.py prd analyze <file> --output db   # Save to database

# Database Management  
uv run python wastask.py db setup                         # Setup database
uv run python wastask.py db list                          # List projects
uv run python wastask.py db show <id>                     # Project details
uv run python wastask.py db stats                         # Statistics

# Migrations
uv run python wastask.py migrate status                   # Migration status
uv run python wastask.py migrate run                      # Run migrations
```

## 📁 Project Structure

```
wastask/
├── wastask.py              # Main CLI entry point
├── setup.py               # Setup script
├── wastask_simple.py      # Core analysis engine
├── agents/                # AI agents for analysis
├── migrations/            # Database migrations
├── docs/                  # All documentation
├── demos/                 # Usage examples
└── tests/                 # Test suite
```

## 📚 Documentation

All documentation is organized in the [`docs/`](docs/) folder:

- **[Getting Started](docs/README.md)** - Complete setup guide
- **[Documentation Index](docs/INDEX.md)** - All docs organized by category
- **[Test Results](docs/test_results.md)** - Validation and examples
- **[Migration System](docs/migrations_implementation_summary.md)** - Database architecture

## 🎉 Example Output

```
🎯 Project: E-commerce Platform
📊 Complexity: 7.2/10
⏱️ Timeline: 12-14 weeks
📈 Total Hours: 406h

🛠️ Recommended Technologies:
  🟢 React Router v7 vlatest
  🟢 PostgreSQL v16.0
  🟢 Drizzle ORM vlatest

📝 Generated Tasks (49 total):
  🔴 High Priority: 12 tasks
  🟡 Medium Priority: 23 tasks
  🟢 Low Priority: 14 tasks
```

## 🗄️ Database

WasTask uses PostgreSQL with a professional migration system:
- Version-controlled schema changes
- Automatic migration execution
- Complete project and task persistence

## 📄 License

MIT License - see LICENSE file for details.

---

🚀 **Ready to transform your PRDs into actionable projects?**  
👉 **Start with**: `python setup.py`