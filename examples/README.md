# Examples Directory

This directory contains example scripts demonstrating how to use FlutterSwarm.

## Prerequisites

- Set up your `.env` file with your Anthropic API key
- Install dependencies: `pip install -r requirements.txt`

## Examples

### basic_usage.py
Demonstrates basic FlutterSwarm usage:
- Creating simple projects (Todo app, E-commerce app)
- Monitoring agent activity
- Understanding build results

### advanced_usage.py  
Shows advanced scenarios:
- Enterprise applications with complex requirements
- Gaming applications with real-time features
- Healthcare applications with compliance requirements
- Performance optimization workflows

## Running Examples

```bash
# Basic examples
python examples/basic_usage.py

# Advanced examples  
python examples/advanced_usage.py

# Interactive CLI
python cli.py interactive
```

## Example Projects

The examples create various types of Flutter applications using **completely LLM-generated code**:

1. **TodoMaster** - Todo app with authentication and collaboration (100% LLM-generated)
2. **ShopifyMobile** - E-commerce app with full payment integration (100% LLM-generated)
3. **EnterpriseHub** - Enterprise app with microservices and compliance (100% LLM-generated)
4. **MultiplayerArena** - Real-time multiplayer gaming app (100% LLM-generated)
5. **HealthVault** - HIPAA-compliant healthcare application (100% LLM-generated)
6. **HighPerformanceApp** - Performance-optimized application (100% LLM-generated)

Each example demonstrates different aspects of the multi-agent system and how agents collaborate to build complete Flutter applications **using only LLM-generated code with ZERO hardcoded templates**.

## Code Generation Philosophy

**CRITICAL:** FlutterSwarm uses a strict LLM-only approach:
- **ZERO hardcoded Flutter templates exist anywhere in the system**
- **ALL Dart/Flutter code is generated by AI agents using LLMs**
- **Tools provide infrastructure, agents provide intelligence**
- **Each agent thinks through problems and generates appropriate code**
- **Code generation is context-aware and adapts to project requirements**
- **Validation system ensures compliance with LLM-only approach**

## Validation

Before running examples, validate the system:

```bash
python validate_system.py
```

This ensures no hardcoded templates exist in the system.
