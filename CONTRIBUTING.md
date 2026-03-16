# Contributing

_This contributing guideline is adapted from the [pyOpenSci Python package template](https://github.com/pyOpenSci/pyos-package-template)._

Contributions of all kinds are welcome here, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Example Contributions

You can contribute in many ways, for example:

- [Report Bugs](#report-bugs)
- [Fix Bugs](#fix-bugs)
- [Implement Features](#implement-features)
- [Write Documentation](#write-documentation)
- [Submit Feedback](#submit-feedback)


### Report Bugs

Report bugs at <https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor/issues>.

### Fix Bugs

Look through the GitHub issues for bugs. Anything labelled with `bug` and
`help wanted` is open to whoever wants to implement it. When you decide to 
work on such an issue, please assign yourself to it and add a comment that 
you'll be working on that, too. If you see another issue without the `help wanted` 
label, just post a comment, the maintainers are usually happy for any support 
that they can get.

### Implement Features

Look through the GitHub issues for features. Anything labelled with
`enhancement` and `help wanted` is open to whoever wants to implement it. 
As for [fixing bugs](#fix-bugs), please assign yourself to the issue and 
add a comment that you'll be working on that, too. If another enhancement 
catches your fancy, but it doesn't have the `help wanted` label, just post 
a comment, the maintainers are usually happy for any support that they can get.

### Write Documentation

Our `walmonitor` could always use more documentation, whether as part of the 
official documentation, in docstrings, or even on the web in blog posts, articles, 
and such. Just [open an issue](https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor/issues) 
to let us know what you will be working on so that we can provide you with guidance.

### Submit Feedback

The best way to send feedback is to file an issue at <https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor/issues>. 

## Get Started

Here's how to set up `walmonitor` for local development.

1. Fork the <https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor> repository on GitHub.

2. Clone your fork locally. Replace `your_name_here` with your GitHub username. 

    ```shell
    git clone git@github.com:your_name_here/DSCI-532_2026_2_walmonitor.git
    ```

3. Install and set up [Conda](https://docs.conda.io/en/latest/) through any
   installer such as [Miniforge](https://conda-forge.org/download/).

4. Create a branch for local development using the `main` branch as a starting point.
   Use `fix` or `feat` as a prefix for your branch name.

    ```shell
    git checkout main
    git checkout -b fix-name-of-your-bugfix
    ```

5. Install the dependencies of this project.

    ```shell
    conda env create -f environment.yml
    conda activate walmonitor
    ```

    Now you can run the app and make your changes locally.

6. When you're done making changes, apply the quality assurance tools and
   check that your changes pass our test suite.

7. Commit your changes and push your branch to GitHub. 

    ```shell
    git add .
    git commit -m "summarize your changes"
    git push -u origin fix-name-of-your-bugfix
    ```

8. Open the link displayed in the message when pushing your new branch
   in order to submit a pull request.

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your
   new functionality into a function with a docstring.
3. Your pull request will automatically be checked by the full test suite.
   It needs to pass all of them before it can be considered for merging.

### Code Style

Your suggested code should follow [PEP 8](https://peps.python.org/pep-0008/) Python style guide. 
We recommend [Ruff](https://docs.astral.sh/ruff/) for automatic code formatting and 
linting. Use straightforward variable names and keep functions focused on one single 
task. Docstrings need to be documented under all functions and class definitions 
using [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html).

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). 
By participating in this project, you agree to abide by its terms.

## Collaboration retrospective

Overall, the collaboration in M3 was very effective, with every team member contributing equally and completing their assigned tasks on time.
#### What worked:
- Every PR was reviewed by at least one team member
- Most PRs had detailed outlines of changes made (which helped make reviewing easier)
#### What didn't work:
- A couple of PRs that implemented many changes were approved without comments (a short comment can help make the process more legible for the whole team)
- A few substantial features were implemented with no design documentation updates

#### Norms for M4:
- Ensure every PR has a detailed outline of changes (and/or mentions an issue that explains the changes) 
- Large PRS (those that implement many important changes) should be approved with a short comment to describe what was checked
- Ensure the design documentation (i.e `m2_spec.md`) is up to date with all features implemented in the dashboard in the previous milestones
- Ensure all substantial features implemented are accompanied with a design documentation update
