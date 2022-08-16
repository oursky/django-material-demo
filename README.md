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
- Run `make start` to start the web server. Then go to http://127.0.0.1:3000/admin to see the demo website
- Run `make migrations` then `make migrate` for model migrations
- Run `make clean` to remove the docker containers
