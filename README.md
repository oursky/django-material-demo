# django-material-demo

## Goal

Demonstrate django admin site common use case.

- Edit page
    - Input type
        - Text / Numeric / Toggle
        - Checkbox
        - Radio button
        - Dropdown with fixed selection
        - Date / Time / Datetime
        - Date / Time range
        - (Multiple) Selection with search
        - File
        - Image
    - Data validation
    - Read-only fields
    - Pre-processing and post-processing
    - Data inputs with dependency
        - Enable / disable checkbox
        - Type dropdown
    - Relational data
        - Inline create and edit
        - Select existing
        - Ordering
    - Translation data
    - Confirmation
    - Multi step form
    - Show edit log / history
- Detail page
- List page
    - Search
        - Search by field
        - Search by field joining other tables
    - Sort
        - Sort by field
        - Sort by field joining other tables
    - Show data by joining other tables
    - Custom actions on data selection

## Initial Setup

1. Run `make setup` to setup docker containers
2. Run `make create-superuser` to create an account to access the admin site

## Dev Workflow
- `cd django_material_demo`
- Run `make -C components start` to build components.
- In another terminal, run `make start` to start the web server. Then go to http://127.0.0.1:3000/polls to see the demo website
- Run `make migrations` then `make migrate` for model migrations
- Run `make clean` to remove the docker containers

## Acknowledgement
- The initial project files are adapted from the "Writing your first Django app" tutorial at https://docs.djangoproject.com/en/4.1/intro/
