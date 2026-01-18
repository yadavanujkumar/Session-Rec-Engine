# Contributing to Session-Rec-Engine

Thank you for your interest in contributing to the Privacy-First Session-Based Recommendation System! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Session-Rec-Engine.git
   cd Session-Rec-Engine
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Install Development Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black flake8 mypy pytest-cov
```

### Start Required Services

```bash
# Option 1: Using Docker Compose
docker-compose up -d redis qdrant

# Option 2: Manual
# Terminal 1: Redis
redis-server

# Terminal 2: Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## Making Changes

### Code Style

We follow PEP 8 and use automated tools:

```bash
# Format code with Black
black src/ tests/

# Check linting with flake8
flake8 src/ tests/ --max-line-length=100

# Type checking (optional)
mypy src/
```

### Writing Tests

- **Location**: Place tests in the `tests/` directory
- **Naming**: Test files should be named `test_*.py`
- **Coverage**: Aim for >80% code coverage for new features

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_models.py::test_sasrec_initialization -v
```

### Commit Messages

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add endpoint for batch recommendations

Add new POST /api/v1/recommend/batch endpoint that accepts
multiple session IDs and returns recommendations for all.

Closes #123
```

```
fix(metrics): resolve deadlock in metrics tracker

Fixed deadlock caused by nested lock acquisition in
get_metrics_summary method.
```

## Areas for Contribution

### High Priority

1. **Additional Models**: Implement BERT4Rec or GRU4Rec
2. **Performance**: Optimize inference latency
3. **Testing**: Increase test coverage
4. **Documentation**: Improve API documentation and examples

### Features

1. **Model Improvements**:
   - Implement additional sequence models
   - Add model ensemble support
   - Implement online learning

2. **API Enhancements**:
   - Batch recommendation endpoint
   - WebSocket support for real-time recommendations
   - GraphQL API

3. **Cold-Start**:
   - Additional bandit algorithms (UCB, Epsilon-Greedy)
   - Context-aware cold-start
   - Hybrid approaches

4. **Observability**:
   - Prometheus metrics exporter
   - Grafana dashboard templates
   - Distributed tracing

5. **Privacy**:
   - Differential privacy mechanisms
   - Federated learning support
   - GDPR compliance tools

### Bug Fixes

Check the [Issues](https://github.com/yadavanujkumar/Session-Rec-Engine/issues) page for known bugs.

## Submitting Changes

### Pull Request Process

1. **Update tests**: Ensure your changes are tested
2. **Update documentation**: Update README.md if needed
3. **Run tests locally**: Make sure all tests pass
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub

### PR Requirements

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] Linting passes (flake8)
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] PR description explains changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted with Black
- [ ] All tests passing
```

## Code Review Process

1. **Automated checks**: GitHub Actions will run tests
2. **Maintainer review**: A maintainer will review your PR
3. **Feedback**: Address any feedback from reviewers
4. **Merge**: Once approved, your PR will be merged

## Project Structure

```
Session-Rec-Engine/
├── src/
│   ├── api/              # FastAPI application
│   ├── models/           # ML models
│   ├── storage/          # Data storage (Redis, Qdrant)
│   ├── coldstart/        # Cold-start handling
│   ├── monitoring/       # Metrics and observability
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration
│   └── service.py        # Main service
├── tests/                # Test suite
├── main.py               # Entry point
├── train.py              # Training script
└── example_usage.py      # Usage examples
```

## Best Practices

### Python

- Use type hints for function signatures
- Write docstrings for public functions
- Keep functions small and focused
- Follow SOLID principles

### Testing

- Write unit tests for all new code
- Use fixtures for common test setup
- Mock external dependencies (Redis, Qdrant)
- Test edge cases and error conditions

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Include examples in docstrings
- Update QUICKSTART.md if setup changes

### Security

- Never commit secrets or credentials
- Validate all user inputs
- Use parameterized queries
- Follow OWASP guidelines

## Questions?

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: Contact maintainers (see README.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute! 🎉
