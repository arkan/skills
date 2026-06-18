---
name: commit-push-pr
description: Commit, push, and open a PR
---

# Git Commit, Push & PR

Workflow complet : commits atomiques → push → PR.

## Étape 1 : Analyse

```bash
git status
git diff --stat
git log origin/main..HEAD --oneline 2>/dev/null || echo "No commits ahead"
```

Identifie :
- Fichiers modifiés/ajoutés/supprimés
- Groupes logiques de changements

## Étape 2 : Commits atomiques

Pour chaque groupe logique de changements :
1. Stage les fichiers concernés : `git add <files>`
2. Commit avec message conventionnel :
   - `feat:` nouvelle fonctionnalité
   - `fix:` correction de bug
   - `refactor:` refactoring sans changement fonctionnel
   - `docs:` documentation
   - `test:` ajout/modification de tests
   - `chore:` maintenance, config

Format du message :
```
<type>: <description courte>

<détails si nécessaire>
```

## Étape 3 : Push

```bash
# Vérifie si la branche a un upstream
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || git push -u origin HEAD
git push
```

## Étape 4 : PR

Vérifie si une PR existe :
```bash
gh pr view --json number 2>/dev/null
```

Si non, crée la PR :
```bash
gh pr create --fill
```

Si oui, affiche le lien de la PR existante.

## Règles

- Ne jamais `--force` push
- Ne jamais modifier l'historique public
- Un commit = un changement logique
- Messages en anglais, style impératif
