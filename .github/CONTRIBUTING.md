# Contributing to NetworkMonitor

Thank you for your interest in contributing to NetworkMonitor! We welcome contributions from everyone.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/networkmonitor.git
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

## Development Process

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following our coding standards:
   - Follow PEP 8 style guide
   - Write descriptive commit messages
   - Include tests for new features
   - Update documentation as needed

3. Test your changes:
   ```bash
   python -m pytest tests/
   ```

4. Push your changes and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

1. Fill out the PR template completely
2. Include tests for new features
3. Update documentation if needed
4. Ensure CI passes
5. Request review from appropriate code owners

## Code Style

- Follow PEP 8 conventions
- Use type hints where possible
- Document public functions and classes
- Keep functions focused and concise
- Write descriptive variable names

## Commit Messages

Format:
```
type(scope): description

[optional body]
[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- style: Code style changes
- refactor: Code changes that neither fix bugs nor add features
- test: Adding or modifying tests
- chore: Maintenance tasks

Example:
```
feat(monitor): add packet filtering by protocol

Added support for filtering network packets by protocol type.
Implements #123
```

## Documentation

- Update README.md for user-facing changes
- Update DEVELOPER.md for development changes
- Add comments for complex code sections
- Include docstrings for public APIs

## Testing

- Write unit tests for new features
- Update existing tests when modifying features
- Include integration tests where appropriate
- Test on all supported platforms if possible

## Release Process

1. Version bumps are handled automatically via GitHub Actions
2. Releases are created from the main branch
3. Changelog is generated automatically
4. Builds are created for all platforms

## Getting Help

- Check existing documentation
- Ask in GitHub Discussions
- Contact maintainers:
  - Umer Farooq (@umerfarok)