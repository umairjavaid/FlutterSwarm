# FlutterSwarm - Multi-Agent Flutter Development System

A sophisticated multi-agent system that collaboratively builds Flutter applications using LangGraph orchestration.

## Overview

FlutterSwarm is an AI-powered development ecosystem where specialized agents work together to create complete Flutter applications. Each agent has specific expertise and all agents maintain shared awareness of the project state.

## Architecture

### Agents

1. **Orchestrator Agent**: Master coordinator managing all agents and workflow
2. **Architecture Agent**: System design and architectural decisions
3. **Implementation Agent**: Flutter/Dart code generation
4. **Testing Agent**: Unit, widget, and integration tests
5. **Security Agent**: Security analysis and best practices
6. **DevOps Agent**: Deployment and CI/CD pipelines
7. **Documentation Agent**: Comprehensive documentation
8. **Performance Agent**: Code optimization and monitoring

### Features

- **Shared State Management**: All agents have real-time awareness of project progress
- **LangGraph Orchestration**: Sophisticated workflow management
- **Collaborative Decision Making**: Agents can communicate and collaborate
- **Complete Flutter Projects**: From architecture to deployment
- **Best Practices**: Security, performance, and code quality built-in

## Requirements

- Python 3.8+
- Anthropic API key (required for AI agents)
- Flutter SDK (for building generated projects)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your Anthropic API key and other required credentials
3. Configure agent settings in `config/agent_config.yaml`

**Note**: FlutterSwarm uses Anthropic's Claude models exclusively for all AI operations.

### Generated Projects

Flutter projects created by FlutterSwarm are saved in the `flutter_projects/` directory. Each project gets its own subdirectory with a complete Flutter application structure. 

**Git Ignore**: Generated projects are automatically excluded from version control (via `.gitignore`) to keep the repository clean, while preserving the `flutter_projects/README.md` file for documentation.

## Usage

```python
from flutter_swarm import FlutterSwarm

# Initialize the swarm
swarm = FlutterSwarm()

# Create a new Flutter project
project = swarm.create_project(
    name="my_flutter_app",
    description="A todo app with user authentication",
    features=["auth", "crud", "offline_sync"]
)

# Let the agents collaborate to build the project
result = await swarm.build_project(project)
```

## Project Structure

```
flutter_swarm/
├── agents/              # Individual agent implementations
├── shared/              # Shared state and communication
├── utils/               # Utility functions (ProjectManager, etc.)
├── config/              # Configuration files
├── examples/            # Example usage scripts
├── flutter_projects/    # Generated Flutter projects (git-ignored)
├── cli.py              # Command-line interface
├── flutter_swarm.py    # Main orchestration system
└── requirements.txt    # Python dependencies
```

## License

MIT License