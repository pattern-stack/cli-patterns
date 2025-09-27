# Pattern Stack Authentication Setup

This document explains how to set up authentication for Pattern Stack repositories to access private dependencies.

## Current Setup: Service Account + PAT

### 1. Create Service Account (One-time per organization)

1. **Create GitHub Account**
   - Create a new GitHub account: `pattern-stack-ci`
   - Use an email like `ci@pattern-stack.com`

2. **Add to Organization**
   - Invite `pattern-stack-ci` to the `pattern-stack` organization
   - Grant `Read` access to repositories that need to be accessed by CI
   - Specifically ensure access to:
     - `pattern-stack/geography-patterns`
     - `pattern-stack/backend-patterns`

### 2. Generate Personal Access Token

1. **Login as Service Account**
   - Login to GitHub as `pattern-stack-ci`

2. **Create PAT**
   - Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - **Name**: `Pattern Stack CI Access`
   - **Expiration**: 1 year (set calendar reminder to rotate)
   - **Scopes**:
     - ✅ `repo` (Full control of private repositories)
   - Generate and copy the token

### 3. Add to Repository Secrets

For each repository that needs access:

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. **Name**: `PATTERN_STACK_TOKEN`
4. **Value**: The PAT from step 2
5. Save

### 4. Verify Setup

The workflows should now:
- Use `PATTERN_STACK_TOKEN` for checkout and git configuration
- Successfully install dependencies from private repositories
- Pass all CI checks

## Auth Pattern Used in Workflows

All workflows use this consistent pattern:

```yaml
steps:
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.PATTERN_STACK_TOKEN }}

- name: Configure git for private repo access
  run: |
    git config --global url."https://x-access-token:${{ secrets.PATTERN_STACK_TOKEN }}@github.com/".insteadOf "https://github.com/"

- name: Install dependencies
  run: |
    uv sync --frozen
    # Dependencies from private repos now work
```

## Future Migration: GitHub App

When scaling to multiple repositories, we'll migrate to a GitHub App approach:

1. **Benefits**: Better security, automatic token rotation, granular permissions
2. **Implementation**: Pattern Stack tooling will automate the creation and installation
3. **Migration**: Seamless - workflows use same `PATTERN_STACK_TOKEN` interface

## Troubleshooting

### Common Issues

1. **"fatal: could not read Username"**
   - Verify `PATTERN_STACK_TOKEN` secret exists in repository
   - Check service account has access to target repositories
   - Verify PAT has `repo` scope

2. **PAT Expired**
   - Generate new PAT with same scopes
   - Update `PATTERN_STACK_TOKEN` secret in all repositories
   - Set calendar reminder for next rotation

3. **403 Forbidden**
   - Service account needs to be added to private repositories
   - Check organization membership and repository access

### Security Notes

- PAT has broad access - rotate regularly (annually)
- Only add to repositories that need private dependency access
- Consider GitHub App migration for better security posture
- Monitor usage in organization audit logs