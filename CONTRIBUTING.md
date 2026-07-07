# Contributing to RFxStarterKit

Thank you for your interest in contributing to RFxStarterKit! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/RFxStarterKit-0.2.git
cd RFxStarterKit-0.2
```

### 2. Set Up Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install all dependencies (runtime + dev tools)
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 3. Configure Environment
```bash
# Copy the master environment template
cp common/.env.template common/.env

# Edit common/.env — at minimum set OPENAI_API_KEY to your
# IBM Services Essentials token (not a personal OpenAI key)
```

### 4. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 guidelines
- **Line Length**: Maximum 100 characters
- **Formatting**: Use `black` for automatic formatting
- **Type Hints**: Add type hints to all function signatures
- **Docstrings**: Add docstrings to all public functions and classes

### Running Code Quality Checks
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_rfp_analyzer.py

# Run with verbose output
pytest -v
```

### Documentation
- Add docstrings to all public functions and classes
- Update README.md if adding new features
- Update CHANGELOG.md with your changes
- Add inline comments for complex logic

### Commit Messages
Follow conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(rfp-analyzer): add support for PDF password protection

docs(readme): update installation instructions for Windows
```

## 🔄 Pull Request Process

### 1. Update Your Branch
```bash
# Fetch latest changes
git fetch upstream
git rebase upstream/master
```

### 2. Run Tests and Checks
```bash
# Ensure all tests pass
pytest

# Run code quality checks
black .
flake8 .
```

### 3. Push Changes
```bash
git push origin feature/your-feature-name
```

### 4. Create Pull Request
- Go to the repository on GitHub
- Click "New Pull Request"
- Select your branch
- Fill in the PR template:
  - **Title**: Clear, descriptive title
  - **Description**: What changes were made and why
  - **Testing**: How the changes were tested
  - **Screenshots**: If applicable
  - **Breaking Changes**: Any breaking changes
  - **Related Issues**: Link to related issues

### 5. Code Review
- Address review comments
- Make requested changes
- Push updates to the same branch
- Request re-review when ready

### 6. Merge
- Once approved, a maintainer will merge your PR
- Delete your feature branch after merge

## 🐛 Reporting Bugs

### Before Reporting
- Check existing issues to avoid duplicates
- Try to reproduce the bug with the latest version
- Gather relevant information

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python Version: [e.g., 3.9.7]
- RFxStarterKit Version: [e.g., 0.1.0]

**Additional context**
Any other relevant information.

**Logs**
```
Paste relevant log output here
```
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Any other context or screenshots.
```

## 📚 Resources

- **Documentation**: See `docs/` directory
- **Quick Start**: See [`docs/QUICK_START.md`](docs/QUICK_START.md)
- **Architecture**: See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **API Reference**: Run the application and visit `/docs`
- **Environment config**: See [`common/.env.template`](common/.env.template)

## 🤝 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

## 📞 Getting Help

If you need help:
1. Check the documentation in `docs/`
2. Search existing issues
3. Ask in discussions
4. Create a new issue with the question label

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to RFxStarterKit! 🚀