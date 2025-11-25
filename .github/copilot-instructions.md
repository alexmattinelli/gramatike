# Gramátike - GitHub Copilot Instructions

## Project Overview

Gramátike is a Flask-based web application for Portuguese grammar education. The platform provides educational content including articles, exercises, podcasts, and study materials for Portuguese language learning.

## Tech Stack

- **Backend**: Flask 3.x, Python 3.12
- **Database**: SQLAlchemy ORM with PostgreSQL (production) or SQLite (development)
- **Frontend**: Jinja2 templates, vanilla JavaScript, Bootstrap
- **Authentication**: Flask-Login with email verification
- **Deployment**: Cloudflare Pages (serverless)
- **Storage**: Cloudflare R2 for file uploads (avatars, PDFs, images)
- **Migrations**: Flask-Migrate (Alembic)

## Coding Standards

### Python Code Style

- Use Python 3.12+ type hints where appropriate
- Follow PEP 8 naming conventions
- Use descriptive variable names in Portuguese when they represent domain concepts (e.g., `usuario`, `conteudo`, `titulo`)
- Keep English for technical/framework terms (e.g., `db`, `app`, `config`)
- Prefer list comprehensions and generator expressions for simple iterations
- Use context managers (`with` statements) for resource management
- Handle exceptions explicitly; avoid bare `except:` clauses

### Flask Patterns

- Register routes using blueprints (see `gramatike_app/routes/__init__.py`)
- Use `@login_required` decorator for protected routes
- Return `render_template()` for HTML responses, `jsonify()` for API endpoints
- Use `current_user` from Flask-Login for authenticated user context
- Implement CSRF protection for forms (Flask-WTF)
- Exempt API endpoints from CSRF when necessary using `@csrf.exempt`

### Database & Models

- Define models in `gramatike_app/models.py`
- Use SQLAlchemy declarative base with `db.Model`
- Add indexes on frequently queried columns (e.g., `created_at`, `tipo`)
- Use `db.relationship()` for foreign key relationships
- Implement soft deletes when appropriate (e.g., `is_deleted` flag)
- Create migrations for schema changes: `flask db migrate -m "description"`
- Always review and test migrations before applying

### Security Best Practices

- Hash passwords using Werkzeug's `generate_password_hash()` and `check_password_hash()`
- Validate and sanitize user inputs
- Use environment variables for sensitive data (see `.env.example`)
- Implement content moderation for user-generated content
- Check user permissions (admin, superadmin) before privileged operations
- Use CSP (Content Security Policy) headers for XSS protection

### Frontend Guidelines

- Use Jinja2 template inheritance (`{% extends %}`, `{% block %}`)
- Keep JavaScript minimal and in separate files under `static/js/`
- Use Bootstrap classes for styling consistency
- Implement progressive enhancement (app works without JS)
- Handle forms with proper CSRF tokens: `{{ csrf_token() }}`
- Use fetch API for AJAX calls, include CSRF header when needed

### File Uploads & Storage

- Use Cloudflare R2 Storage for file uploads (avatars, PDFs, images)
- Generate unique file paths with timestamps: `avatars/{user_id}/{timestamp}_{filename}`
- Use helper functions from `gramatike_app/utils/storage.py`:
  - `build_avatar_path()` for user avatars
  - `build_post_image_path()` for post images
  - `build_apostila_path()` for PDF study materials
  - `build_divulgacao_path()` for promotional content
- Validate file types and sizes before upload
- Configure R2 bucket for public read access

### Environment Variables

Required environment variables (see README.md):
- `SECRET_KEY`: Flask secret key (32+ chars)
- `DATABASE_URL`: PostgreSQL connection string (production)
- `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_R2_ACCESS_KEY_ID`, `CLOUDFLARE_R2_SECRET_ACCESS_KEY`, `CLOUDFLARE_R2_BUCKET`: File storage
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Email configuration
- `RAG_MODEL`: Optional AI/embeddings model

Always use `os.environ.get()` with sensible defaults where appropriate.

### Database Configuration

- The app auto-detects database URLs and normalizes them
- Handles both `postgres://` and `postgresql://` schemes
- Configures connection pooling for serverless (small pool size)
- Uses `pool_pre_ping=True` for connection health checks
- SQLite fallback for local development

### Serverless Considerations (Cloudflare Pages)

- Keep functions lightweight and stateless
- Database connections are pooled with small pool size (1-2)
- Use Cloudflare R2 or external storage (not local filesystem) for uploads
- Environment variables set in Cloudflare Pages dashboard
- Entry point: `api/index.py` exposes Flask app

### Testing & Validation

- Test database migrations: `flask db upgrade` then `flask db downgrade`
- Verify CSRF tokens in forms
- Test with both admin and regular users
- Check responsive design on mobile devices
- Validate email sending in development mode
- Test file upload limits (MAX_CONTENT_LENGTH)

### Language & Localization

- Primary language: Portuguese (Brazil)
- Use Portuguese for:
  - User-facing messages, labels, and content
  - Database field names representing domain concepts
  - Template variables and form labels
  - Comments describing business logic
- Use English for:
  - Technical/framework code and variables
  - Library imports and technical documentation
  - Git commit messages (can be in Portuguese or English)

### Error Handling

- Log errors using `current_app.logger.error()` or `current_app.logger.warning()`
- Provide user-friendly error messages in Portuguese
- Handle database connection errors gracefully (serverless context)
- Return appropriate HTTP status codes (404, 403, 500, etc.)
- Use try/except blocks for external API calls (email, storage)

### Code Organization

- **Models**: `gramatike_app/models.py` - Database models
- **Routes**: `gramatike_app/routes/__init__.py` - Main route handlers
- **Forms**: `gramatike_app/forms.py` - WTForms definitions
- **Templates**: `gramatike_app/templates/` - Jinja2 HTML templates
- **Static files**: `gramatike_app/static/` - CSS, JS, images
- **Utils**: `gramatike_app/utils/` - Helper functions (storage, moderation, agent)
- **Config**: `config.py` - Application configuration
- **Migrations**: `migrations/versions/` - Database migrations

### Common Patterns to Follow

1. **User Authentication Check**:
   ```python
   if not current_user.is_authenticated:
       return redirect(url_for('main.login'))
   ```

2. **Admin Permission Check**:
   ```python
   is_admin = getattr(current_user, 'is_authenticated', False) and (
       getattr(current_user, 'is_admin', False) or 
       getattr(current_user, 'is_superadmin', False)
   )
   ```

3. **Template Rendering with Context**:
   ```python
   return render_template('template.html', 
       title='Page Title',
       data=data,
       is_admin=is_admin
   )
   ```

4. **File Upload to Cloudflare R2**:
   ```python
   from gramatike_app.utils.storage import upload_to_storage, build_avatar_path
   
   file_path = build_avatar_path(user_id, filename)
   url = upload_to_storage(file_path, file_data, content_type)
   ```

5. **Database Query with Error Handling**:
   ```python
   try:
       items = Model.query.filter_by(field=value).all()
   except Exception as e:
       current_app.logger.error(f"Query failed: {e}")
       items = []
   ```

### Documentation Conventions

- Create comprehensive documentation for major features (see examples: `IMPLEMENTATION_COMPLETE.md`, `VISUAL_CHANGES_GUIDE.md`)
- Include before/after comparisons for UI changes
- Document environment variables and configuration
- Provide step-by-step testing instructions
- Use checklists for deployment and validation
- Include troubleshooting sections when applicable

### Git & Deployment

- Keep commits focused and atomic
- Write clear commit messages describing the change
- Test locally before pushing
- Create migrations for schema changes
- Update documentation when changing features
- Review `.gitignore` to exclude build artifacts, `.env` files, and `__pycache__`

### AI/Agent Integration

- The app includes an agent-based response system (`gramatike_app/utils/agent_core.py`)
- Agents provide Portuguese grammar assistance with:
  - Direct answers without preambles
  - Step-by-step explanations when requested
  - Concrete examples for clarity
- Follow the pattern: plan → reflect → apply suggestions

### Content Types in EduContent Model

The `EduContent` model supports multiple content types:
- `artigo` - Articles
- `apostila` - Study materials (PDFs)
- `podcast` - Podcast links
- `exercicio` - Exercise metadata
- `redacao_tema` - Essay topics
- `variacao` - Linguistic variation content

Use the `tipo` field to filter content by type.

## When Making Changes

1. **Understand the context**: Review related code before making changes
2. **Follow existing patterns**: Match the style and structure of existing code
3. **Test thoroughly**: Verify database operations, form submissions, and user flows
4. **Update documentation**: Keep README.md and feature docs current
5. **Consider serverless**: Remember the Cloudflare Pages deployment constraints
6. **Validate security**: Check permissions, CSRF protection, and input validation
7. **Handle errors**: Add appropriate logging and user-friendly error messages
8. **Keep it minimal**: Make the smallest necessary changes to achieve the goal
