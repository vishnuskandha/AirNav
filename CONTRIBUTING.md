# Contributing to AirNav

Thank you for your interest in contributing to AirNav! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details**: Python version, OS, webcam specs
- **Screenshots or logs** if applicable

### Suggesting Enhancements

Feature requests are welcome! Please:
- Check existing issues to avoid duplicates
- Describe the feature clearly
- Explain **why** it would be useful
- Provide examples or mockups if applicable

### Pull Request Process

1. **Fork the repository** and create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines (below)

3. **Test your changes**:
   - Ensure the app runs without errors
   - Test on your webcam hardware
   - Verify face enrollment and gesture recognition still work

4. **Update documentation**:
   - Update README.md if you added features or changed usage
   - Add docstrings to new functions/classes
   - Update requirements.txt if you added dependencies

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "Add feature: description of what you did"
   ```

6. **Push to your fork** and create a pull request:
   - Provide a clear title and description
   - Reference any related issues (e.g., "Fixes #123")
   - Explain what you changed and why

## Code Style Guidelines

- **Follow PEP 8** for Python code
- **Use meaningful variable names** (avoid single-letter variables except in loops)
- **Add comments** for complex logic
- **Keep functions focused** — each function should do one thing well
- **Use type hints** where applicable

### Example:
```python
def calculate_distance(point1: tuple, point2: tuple) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: (x, y) coordinates of first point
        point2: (x, y) coordinates of second point
    
    Returns:
        Distance as a float
    """
    return np.hypot(point1[0] - point2[0], point1[1] - point2[1])
```

## Testing Requirements

Before submitting a PR, ensure:
- [ ] App starts without errors (`python modern_app.py`)
- [ ] Face enrollment works (`python enroll_face.py`)
- [ ] Face authentication works
- [ ] Gesture tracking is responsive
- [ ] No new warnings or errors in console
- [ ] Works on Windows (Linux/macOS if you have access)

## Development Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AirNav.git
   cd AirNav
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Test your setup**:
   ```bash
   python enroll_face.py  # Enroll your face
   python modern_app.py   # Launch the app
   ```

## Communication

- **GitHub Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For general questions and ideas

## License

By contributing to AirNav, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AirNav! 🚀
