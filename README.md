# Ministry of Justice Operations Engineering Main Repo

[![repo standards badge](https://img.shields.io/badge/dynamic/json?color=blue&style=for-the-badge&logo=github&label=MoJ%20Compliant&query=%24.result&url=https%3A%2F%2Foperations-engineering-reports.cloud-platform.service.justice.gov.uk%2Fapi%2Fv1%2Fcompliant_public_repositories%2Foperations-engineering)](https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/public-github-repositories.html#operations-engineering "Link to report")

## About this Repository

This is the MoJ Operations Engineering team's repository for public facing documentation, feature work, enhancements, and issues.

**The docs folder is used by the gh-pages branch to host the website. Do not delete.**

## Website

The website is designed using the [Technical Documentation Template](https://tdt-documentation.london.cloudapps.digital/)

This repository is published via Github Pages [here](https://ministryofjustice.github.io/operations-engineering/#moj-operations-engineering)

To update, edit files in [this directory](https://github.com/ministryofjustice/operations-engineering/tree/main/source). To run the site locally while editing, make sure you have docker running and then run `make` in the root folder of the repository. The site will auto-reload on changes.

The config/tech-docs.yml file contains layout configuration options see [link](https://tdt-documentation.london.cloudapps.digital/configure_project/global_configuration/) for more details.
