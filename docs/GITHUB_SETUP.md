# GitHub setup for the first public push

This project already contains a Git history. Create an **empty** repository on GitHub and push the existing history.

## 1. Create the repository on GitHub

Suggested repository name: `familienakte`

- Visibility: Public (or Private first, then switch to Public later)
- Do **not** initialize with README, `.gitignore`, or License

## 2. Configure SSH on the server

Check for an existing key:

```bash
ls -la ~/.ssh
```

If no suitable Ed25519 key exists:

```bash
ssh-keygen -t ed25519 -C "YOUR_GITHUB_EMAIL"
```

Then show the public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Add that public key in GitHub under **Settings → SSH and GPG keys → New SSH key**.

Test the connection:

```bash
ssh -T git@github.com
```

## 3. Add GitHub as remote

Inside this repository:

```bash
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/familienakte.git
```

Verify:

```bash
git remote -v
```

## 4. Push code and tags

```bash
git push -u origin main
git push origin --tags
```

## 5. Recommended repository settings

- Enable Issues
- Enable private vulnerability reporting if available
- Add a short repository description and topics
- Consider branch protection/rules for `main` later
- Create a GitHub Release from the latest stable tag when ready

## 6. Before publishing screenshots

Use demo data only. Never publish real family names, profile photos, medical records, backups, hostnames, IP addresses, or credentials.
