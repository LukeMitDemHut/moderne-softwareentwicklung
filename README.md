# Git-Handout für Anfänger

Dieses Handout erklärt die wichtigsten Grundlagen von Git: wofür man es braucht, welche Befehle man täglich nutzt, wie man mit Branches und Merge-Konflikten umgeht und wie man Git in IntelliJ bzw. PyCharm verwendet.

## Inhaltsverzeichnis

1. [Was ist Git und warum sollte man es verwenden?](#1-was-ist-git-und-warum-sollte-man-es-verwenden)
2. [Grundlegende Git-Befehle](#2-grundlegende-git-befehle)
3. [Branches und Merge-Konflikte](#3-branches-und-merge-konflikte)
4. [Git mit IntelliJ / PyCharm](#4-git-mit-intellij--pycharm)
5. [Nützliche Git-Tools und Plattformen](#5-nützliche-git-tools-und-plattformen)

---

## 1. Was ist Git und warum sollte man es verwenden?

### Was ist Git?

Git ist ein **verteiltes Versionskontrollsystem**. Es speichert die Geschichte eines Projekts als Folge von **Commits** (Schnappschüsse des Projektzustands). Jede:r Entwickler:in hat dabei eine vollständige Kopie des Repositorys inklusive der gesamten Historie auf dem eigenen Rechner.

Wichtige Begriffe:

| Begriff | Bedeutung |
|---|---|
| **Repository (Repo)** | Projektordner inklusive der gesamten Versionshistorie (im versteckten Ordner `.git`) |
| **Commit** | Gespeicherter Zustand des Projekts mit Nachricht, Autor:in und Zeitstempel |
| **Branch** | Eigenständiger Entwicklungszweig, in dem unabhängig gearbeitet werden kann |
| **Remote** | Version des Repositorys auf einem Server, z. B. auf GitHub (meist `origin` genannt) |
| **Clone** | Lokale Kopie eines Remote-Repositorys |
| **Merge** | Zusammenführen der Änderungen aus zwei Branches |
| **Pull Request (PR)** | Anfrage, Änderungen aus einem Branch in einen anderen zu übernehmen, inkl. Review |

### Warum sollte man Git verwenden?

- **Nachvollziehbarkeit:** Jede Änderung ist dokumentiert: wer hat was wann und warum geändert?
- **Rückgängig machen:** Fehler lassen sich beheben, indem man zu einem früheren Stand zurückkehrt.
- **Teamarbeit:** Mehrere Personen können gleichzeitig am selben Projekt arbeiten, ohne sich gegenseitig Dateien zu überschreiben.
- **Experimentieren ohne Risiko:** In eigenen Branches kann man Neues ausprobieren, ohne den funktionierenden Stand zu gefährden.
- **Backup:** Durch das Remote-Repository liegt der Code zusätzlich auf einem Server.
- **Industriestandard:** Git ist in der Softwareentwicklung praktisch überall im Einsatz.

---

## 2. Grundlegende Git-Befehle

### Einrichtung (einmalig)

```bash
git config --global user.name "Dein Name"
git config --global user.email "deine.mail@example.com"
```

### Repository anlegen oder klonen

```bash
git init                      # Neues, leeres Repository im aktuellen Ordner anlegen
git clone <URL>               # Bestehendes Remote-Repository lokal kopieren
```

### Der tägliche Workflow

```bash
git status                    # Zeigt geänderte, neue und gestagte Dateien
git add <datei>               # Einzelne Datei zur Staging Area hinzufügen
git add .                     # Alle Änderungen im aktuellen Ordner hinzufügen
git commit -m "Nachricht"     # Gestagte Änderungen als Commit speichern
git push                      # Lokale Commits zum Remote-Repository hochladen
git pull                      # Änderungen vom Remote holen und in den lokalen Branch einbauen
```

### Verlauf und Änderungen ansehen

```bash
git log                       # Commit-Historie anzeigen
git log --oneline --graph     # Kompakte Historie mit Branch-Graph
git diff                      # Noch nicht gestagte Änderungen anzeigen
git diff --staged             # Gestagte Änderungen anzeigen
```

### Änderungen rückgängig machen

```bash
git restore <datei>           # Änderungen in einer Datei im Arbeitsverzeichnis verwerfen
git restore --staged <datei>  # Datei wieder aus der Staging Area nehmen
git revert <commit>           # Neuen Commit erzeugen, der einen früheren Commit rückgängig macht
```

> **Achtung:** `git restore <datei>` verwirft ungespeicherte Änderungen endgültig.

---

## 3. Branches und Merge-Konflikte

### Was sind Branches?

Ein **Branch** ist ein beweglicher Zeiger auf einen Commit. Er erlaubt es, parallel an mehreren Dingen zu arbeiten, z. B. an einem neuen Feature, ohne den Hauptzweig (`main`) zu verändern.

```
main:     A --- B --- C ----------- F  (Merge)
                       \           /
feature:                D --- E --
```

### Branch-Befehle

```bash
git branch                    # Alle lokalen Branches anzeigen (* = aktueller Branch)
git branch <name>             # Neuen Branch anlegen
git switch <name>             # Zu einem Branch wechseln
git switch -c <name>          # Neuen Branch anlegen und direkt wechseln
git merge <name>              # Branch <name> in den aktuellen Branch mergen
git branch -d <name>          # Gemergten Branch löschen
git push -u origin <name>     # Neuen Branch zum Remote hochladen (und verknüpfen)
```

### Typischer Branch-Workflow im Team

1. Aktuellen Stand holen: `git switch main` und `git pull`
2. Eigenen Branch anlegen: `git switch -c feature/mein-abschnitt`
3. Änderungen machen und in mehreren Commits speichern
4. Branch hochladen: `git push -u origin feature/mein-abschnitt`
5. Auf GitHub/GitLab einen **Pull Request** erstellen
6. Teammitglieder prüfen den PR (**Review**) und geben Feedback
7. Nach Freigabe wird der PR in `main` **gemergt**

### Merge-Konflikte

Ein **Merge-Konflikt** entsteht, wenn zwei Branches **dieselbe Stelle** einer Datei unterschiedlich geändert haben und Git nicht entscheiden kann, welche Version gelten soll. Das ist normal und kein Fehler.

So sieht ein Konflikt in der Datei aus:

```
<<<<<<< HEAD
Dies ist die Version aus deinem aktuellen Branch.
=======
Dies ist die Version aus dem Branch, der gemergt wird.
>>>>>>> feature/anderer-branch
```

**Konflikt lösen, Schritt für Schritt:**

1. `git status` zeigt, welche Dateien betroffen sind (`both modified`).
2. Datei öffnen und die Markierungen `<<<<<<<`, `=======` und `>>>>>>>` suchen.
3. Entscheiden: eigene Version behalten, fremde Version übernehmen oder beide kombinieren.
4. Die Markierungen komplett entfernen.
5. Datei hinzufügen und den Merge abschließen:
   ```bash
   git add <datei>
   git commit
   ```

**Konflikte vermeiden:**

- Häufig `git pull` ausführen, damit man auf dem aktuellen Stand bleibt
- Branches klein und kurzlebig halten
- Im Team absprechen, wer an welchen Dateien bzw. Abschnitten arbeitet

Möchte man einen Merge abbrechen, geht das mit `git merge --abort`.

---

## 4. Git mit IntelliJ / PyCharm

IntelliJ IDEA und PyCharm (beide von JetBrains) haben Git direkt integriert, sodass man die meisten Aufgaben ohne Kommandozeile erledigen kann. Die Menüs können je nach Version leicht abweichen.

### Repository klonen

- **Startbildschirm:** `Get from VCS` bzw. `Clone Repository`
- **Im geöffneten Projekt:** `Git` → `Clone…` (bzw. `File` → `New` → `Project from Version Control`)
- URL des Repositorys einfügen, Zielordner wählen, `Clone` klicken

### Bestehendes Projekt unter Versionskontrolle stellen

- `Git` → `Create Git Repository…` (bzw. `VCS` → `Enable Version Control Integration…`) und Git auswählen. Das entspricht `git init`.

### Local Repository: Änderungen committen

1. Das **Commit-Fenster** öffnen (Seitenleiste links oder `Strg+K` bzw. `Cmd+K`).
2. Geänderte Dateien per Häkchen auswählen. Das entspricht `git add`.
3. **Commit-Nachricht** eingeben.
4. `Commit` klicken. Mit `Commit and Push…` wird direkt hochgeladen.

Farbcodes im Projektbaum: **grün** = neue Datei, **blau** = geänderte Datei, **grau** = von `.gitignore` ignoriert.

### Remote Repository: Push, Pull und Fetch

| Aktion | Wo in der IDE | Entspricht |
|---|---|---|
| **Push** | `Git` → `Push…` oder `Strg+Shift+K` | `git push` |
| **Pull** | `Git` → `Pull…` | `git pull` |
| **Fetch** | `Git` → `Fetch` | `git fetch` |
| **Remote hinzufügen** | `Git` → `Manage Remotes…` | `git remote add` |

Beim Verbinden mit GitHub kann man sich über `Settings` → `Version Control` → `GitHub` mit dem Account anmelden (oder per Personal Access Token).

### Branches in der IDE

- Der **Branch-Name** wird in der Hauptleiste (oben) bzw. unten rechts in der Statusleiste angezeigt. Ein Klick darauf öffnet das Branch-Menü.
- **New Branch…** legt einen neuen Branch an (`git switch -c`).
- **Checkout** wechselt den Branch.
- **Merge into Current** führt einen anderen Branch in den aktuellen zusammen.
- Das Tool-Fenster **Git** (Tab `Log`) zeigt die Historie samt Branch-Graph.

---

## 5. Nützliche Git-Tools und Plattformen

### Hosting-Plattformen

| Plattform | Beschreibung |
|---|---|
| **[GitHub](https://github.com)** | Größte Plattform mit Pull Requests, Issues, GitHub Actions (CI/CD), Projects und Pages |
| **[GitLab](https://gitlab.com)** | Ähnlicher Funktionsumfang, dort heißen PRs *Merge Requests*; auch selbst hostbar |

### Praktische Werkzeuge

- **GitHub CLI (`gh`):** PRs und Issues direkt im Terminal erstellen, z. B. `gh pr create`
- **GitHub Desktop:** Einfache grafische Oberfläche für Einsteiger
- **GitKraken, Sourcetree:** Grafische Git-Clients mit übersichtlicher Branch-Darstellung
- **Git in VS Code:** Integrierte Versionskontrolle (Source-Control-Ansicht)

### Weitere nützliche Features

- **Issues:** Aufgaben, Bugs und Ideen im Team verwalten
- **Pull-Request-Reviews:** Änderungen kommentieren, Verbesserungen vorschlagen und freigeben
- **Branch Protection:** Auf `main` darf nur noch über freigegebene PRs gemergt werden
- **GitHub Actions / GitLab CI:** Tests und Builds automatisch bei jedem Push ausführen
- **`git stash`:** Unfertige Änderungen kurz zur Seite legen (`git stash`, später `git stash pop`)

