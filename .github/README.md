# GitHub Configuration

This directory contains GitHub-specific configuration files for the Gramátike repository.

## Files

### copilot-instructions.md

Custom instructions for GitHub Copilot coding agent. This file helps Copilot understand:

- **Project architecture**: Flask-based web app for Portuguese grammar education
- **Tech stack**: Flask 3.x, Python 3.12, SQLAlchemy, Jinja2, Vercel deployment
- **Coding standards**: Python style, Flask patterns, database conventions
- **Security practices**: Authentication, CSRF protection, input validation
- **File organization**: Models, routes, templates, static files, utilities
- **Common patterns**: Code examples for authentication, admin checks, file uploads, database queries
- **Deployment considerations**: Serverless constraints, environment variables, connection pooling

## Purpose

The `copilot-instructions.md` file ensures that GitHub Copilot provides:
- Contextually appropriate code suggestions
- Consistent coding style across the project
- Security-conscious implementations
- Framework-specific best practices
- Proper error handling and logging

## Updating Instructions

When making significant architectural changes to the repository:
1. Review and update `copilot-instructions.md`
2. Add new patterns or conventions
3. Update tech stack information if dependencies change
4. Document new coding standards or security practices

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Custom Instructions Guide](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [Best Practices for Copilot Coding Agent](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
