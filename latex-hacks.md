# 📚 LaTeX Hacks — The Ultimate Academic Survival Guide

_A practical handbook for theses, papers, presentations, posters, and research documents._

---

## 🧭 Table of Contents

1. [General Principles](#general-principles)
2. [Document Setup](#document-setup)
3. [Typography & Layout Hacks](#typography--layout-hacks)
4. [Math Hacks](#math-hacks)
5. [Tables That Don’t Suck](#tables-that-dont-suck)
6. [Figures, Images & Floats](#figures-images--floats)
7. [References & Bibliographies](#references--bibliographies)
8. [Algorithms & Pseudocode](#algorithms--pseudocode)
9. [Plots, Code Snippets & Data](#plots-code-snippets--data)
10. [Slides, Posters & CVs](#slides-posters--cvs)
11. [Debugging LaTeX](#debugging-latex)
12. [Common Boilerplates](#common-boilerplates)
13. [Ultimate Packages List](#ultimate-packages-list)

---

## 1. General Principles

### ✔ Compile at least **twice**

LaTeX resolves references on the second pass.

### ✔ Never fight LaTeX line-breaking manually

Avoid `\\` inside text paragraphs. Use `\linebreak` or `\newline`

### ✔ Keep your preamble clean

Use `latexmk` or VS Code LaTeX Workshop for auto builds.

---

## 2. Document Setup

### Minimal modern setup

```tex
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}

\usepackage{microtype}  % Beautiful typography
\usepackage{graphicx}   % Images
\usepackage{xcolor}     % Colors
\usepackage{hyperref}   % Hyperlinks
\usepackage{amsmath, amssymb, amsthm}  % Math
\usepackage{xurl}       % Better URL breaking
```

---

## 3. Typography & Layout Hacks

### Fixing overfull hboxes (the eternal problem)

1. Add global flexibility:

   ```tex
   \emergencystretch=3em
   ```

2. Enable micro-typography:

   ```tex
   \usepackage{microtype}
   ```

3. Allow breakpoints:

   ```tex
   verylongword\allowbreak moretext
   ```

4. Hyphenate unusual words:

   ```tex
   \hyphenation{auto-mata-theory trans-form-ation}
   ```

---

### Inline units & spacing

Use `siunitx`:

```tex
\usepackage{siunitx}
```

Examples:

```tex
\SI{9.81}{\meter\per\second\squared}
\SI{3e8}{\meter\per\second}
```

---

### Prevent widows/orphans (single lines at page top/bottom)

```tex
\clubpenalty=10000
\widowpenalty=10000
```

---

### Suchen und ersetzen aus KI

To change from $$ to \[]\:

```regex
\$\$([\s\S]*?)\$\$
\\[$1\\]
```

To change from "..." to ``...'':

```
"(.*?)"
``$1''
```

## 4. Math Hacks

### Best environments (forget `eqnarray`!)

```tex
\begin{align}
a &= b + c \\
d &= e - f
\end{align}
```

To break long inline math:

```tex
A = B + \allowbreak C + D
```

### Define your operators

```tex
\DeclareMathOperator{\argmax}{argmax}
```

### Bold vectors

```tex
\mathbf{v}
\boldsymbol{\theta}
```

### Blackboard bold

```tex
\mathbb{R}, \mathbb{N}, \mathbb{E}
```

---

## 5. Tables That Don’t Suck

### Use `booktabs`

```tex
\usepackage{booktabs}
```

Example:

```tex
\begin{tabular}{lcc}
\toprule
Method & Accuracy & Time \\
\midrule
A & 92\% & 3s \\
B & 94\% & 5s \\
\bottomrule
\end{tabular}
```

---

### Auto-width tables (`tabularx`)

```tex
\usepackage{tabularx}

\begin{tabularx}{\linewidth}{lX}
Label & This column stretches automatically. \\
\end{tabularx}
```

---

## 6. Figures, Images & Floats

### Best float setup

```tex
\usepackage{graphicx}
\usepackage{caption}
\usepackage{subcaption}
```

### Figure template

```tex
\begin{figure}[ht]
  \centering
  \includegraphics[width=.8\linewidth]{plot.pdf}
  \caption{My awesome figure.}
  \label{fig:myfig}
\end{figure}
```

### Prevent float chaos

```tex
\usepackage{float}
```

Then:

```tex
\begin{figure}[H]  % absolutely HERE
```

---

## 7. References & Bibliographies

### Hyperref configuration (standard)

```tex
\usepackage[hidelinks]{hyperref}
```

### Best bibliography workflow: **biblatex + biber**

```tex
\usepackage[
    backend=biber,
    style=authoryear,
    maxbibnames=99
]{biblatex}

\addbibresource{refs.bib}
```

Cite:

```tex
\parencite{Smith2020}
\textcite{Smith2020}
```

---

## 8. Algorithms & Pseudocode

Use `algorithm2e`:

```tex
\usepackage[ruled,vlined]{algorithm2e}
```

Example:

```tex
\begin{algorithm}
\SetAlgoLined
\KwIn{Graph $G$}
\KwOut{Distances}
...
\end{algorithm}
```

Or `algorithmicx`:

```tex
\usepackage{algorithm}
\usepackage{algpseudocode}
```

---

## 9. Plots, Code Snippets & Data

### Beautiful plots

- Best: generate plots in Python/Matplotlib or TikZ externalize.

#### TikZ/PGFPlots

```tex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

---

### Code highlighting (`minted`)

Requires `--shell-escape`.

```tex
\usepackage{minted}

\begin{minted}{python}
def hello():
    print("hi")
\end{minted}
```

---

## 10. Slides, Posters & CVs

### Slides: **Beamer**

```tex
\documentclass{beamer}
```

### Scientific posters

- `tikzposter`
- `beamerposter`

### CVs

- `moderncv`

---

## 11. Debugging LaTeX

### See exactly where errors occur

```tex
\errorcontextlines=999
```

### Common problems

| Error                      | Meaning                 | Fix                                      |
| -------------------------- | ----------------------- | ---------------------------------------- |
| Overfull \hbox             | line too long           | microtype, emergencystretch, hyphenation |
| Missing }                  | unbalanced braces       | check previous lines                     |
| Misplaced \noalign         | broken table            | fix missing `\\` or extra `&`            |
| Undefined control sequence | typo or missing package | load required package                    |

---

## 12. Common Boilerplates

### Theorem setup

```tex
\usepackage{amsthm}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{definition}{Definition}
```

---

### Custom commands

```tex
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\norm}[1]{\left\lVert #1 \right\rVert}
```

---

## 13. Ultimate Packages List

### Essential

```text
microtype    – Makes text spacing and justification look professional; reduces overfull hboxes.
graphicx     – Insert images; controls scaling, rotation, cropping.
xcolor       – Defines colors; needed for colored text, boxes, links, tables, plots.
hyperref     – Makes references and URLs clickable; handles PDF metadata.
xurl         – Allows URLs to break across lines (critical for long links).
amsmath      – Essential math environments (align, gather, multline).
amssymb      – Extra math symbols (ℝ, ℕ, ∀, ∅, etc.).
amsthm       – Theorem-like environments (theorem, lemma, definition).
siunitx      – Proper scientific units, numbers, tables (SI units, align decimals).
booktabs     – Professional table rules (toprule, midrule, bottomrule).
tabularx     – Auto-stretching table columns to full text width.
mathtools    – Extensions to amsmath (aligned equations, cases*, smallmatrix*).
```

### Advanced / optional

```text
algorithm2e  – Beautiful pseudocode environments for algorithms.
minted       – Syntax-highlighted code listings (requires --shell-escape).
pgfplots     – High-quality plots directly in LaTeX using TikZ.
tikz         – Vector graphics, diagrams, automata, flowcharts, trees.
cleveref     – Smart cross-referencing (“Figure 3”, “Theorem 4”) without manual prefixes.
subcaption   – Subfigures with (a), (b), (c) captions.
enumitem     – Fine control over lists (spacing, labeling, alignment).
csquotes     – Language-aware quotation marks; integrates with biblatex.
biblatex     – Modern bibliography management (with Biber); replaces BibTeX.
titlesec     – Customize section titles (spacing, fonts, formatting).
fancyhdr     – Custom header and footer layout.
float        – Adds the H specifier: force figures/tables exactly HERE.
```
