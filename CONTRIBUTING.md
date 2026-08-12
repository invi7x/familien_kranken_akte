# Contributing to Familienakte

Thanks for helping improve Familienakte.

## Before opening an issue

- Check whether the problem already exists in the issue tracker.
- Use a current release when reproducing a bug.
- Never attach real health records, JSON backups, profile photos, credentials, hostnames, or other personal data.

## Bug reports

Please include:

- Familienakte version
- Docker / Docker Compose version
- browser and device
- steps to reproduce
- expected behavior
- actual behavior
- relevant log excerpt with personal data removed

## Feature requests

Describe the use case first. A feature is more useful when the problem it solves is clear.

## Pull requests

1. Create a branch from `main`.
2. Keep changes focused on one topic.
3. Test the Docker build and the affected UI paths.
4. Keep JSON import/export backwards-compatible whenever possible.
5. Update `CHANGELOG.md` when a user-visible change is introduced.
6. Do not add dependencies unless they provide clear value.

By contributing code, you agree that your contribution is licensed under the repository's MIT License.
