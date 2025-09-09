# Setting Up Branch Protection Rules

This document explains how to set up branch protection rules for the `release/**` branches and ensure they are properly protected as required by issue requirements.

## Automated Setup (Recommended)

### Using GitHub CLI

1. Install and authenticate GitHub CLI:
   ```bash
   # Install gh CLI (if not already installed)
   # For Ubuntu/Debian: sudo apt install gh
   # For macOS: brew install gh
   
   # Authenticate
   gh auth login
   ```

2. Apply branch protection for release branches:
   ```bash
   # Set protection for release/** pattern
   gh api repos/johnnymillergh/python-web-service-boilerplate/branches/release*/protection \
     --method PUT \
     --field required_status_checks='{"strict":true,"contexts":["code-quality-check","fastapi-smoke-testing","check-versions"]}' \
     --field enforce_admins=true \
     --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
     --field restrictions=null \
     --field allow_force_pushes=false \
     --field allow_deletions=false
   ```

### Using Terraform (for Infrastructure as Code)

```hcl
resource "github_branch_protection" "release_branches" {
  repository_id = "python-web-service-boilerplate"
  pattern       = "release/**"

  required_status_checks {
    strict   = true
    contexts = ["code-quality-check", "fastapi-smoke-testing", "check-versions"]
  }

  enforce_admins = true

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
    require_code_owner_reviews     = false
  }

  allow_force_pushes = false
  allows_deletions   = false
}
```

## Manual Setup via GitHub Web Interface

1. Navigate to the repository: `https://github.com/johnnymillergh/python-web-service-boilerplate`
2. Go to **Settings** → **Branches**
3. Click **Add rule**
4. Configure the following:

   - **Branch name pattern**: `release/**`
   - **Protect matching branches**: ✅ checked
   - **Require a pull request before merging**: ✅ checked
     - **Require approvals**: 1
     - **Dismiss stale PR approvals when new commits are pushed**: ✅ checked
   - **Require status checks to pass before merging**: ✅ checked
     - **Require branches to be up to date before merging**: ✅ checked
     - **Status checks**: Add these required checks:
       - `code-quality-check`
       - `fastapi-smoke-testing` 
       - `check-versions`
   - **Require conversation resolution before merging**: ✅ checked
   - **Restrict pushes that create matching branches**: ⬜ unchecked
   - **Allow force pushes**: ⬜ unchecked (disabled)
   - **Allow deletions**: ⬜ unchecked (disabled)

5. Click **Create**

## Verification

After setting up the protection rules, verify they work by:

1. Creating a test release branch:
   ```bash
   git checkout -b release/test-protection
   git push origin release/test-protection
   ```

2. Try to push directly to the branch (should be blocked if configured correctly)
3. Create a pull request to test the review and status check requirements

## Troubleshooting

- **Status checks not available**: Ensure the CI workflow has run at least once on the repository
- **Insufficient permissions**: Repository admin access is required to set up branch protection
- **Pattern not matching**: Make sure the pattern `release/**` matches your branch naming convention