# Data Model

## File

- file_id, string
- storage_loc, string
- file_name, string (100 max)
- file_type, string
- file_size, int

## User

- name, string (50 max)
- email, string (100 max)
- group, choice (default, subscriber, super admin)
- subs_start (subscription start date), date (subscriber only)
- subs_expire (subscription expire date), date (subscriber only)
- followers, ManyToManyFieid to User

## Question

- question_text, string (200 max)
- total_vote_count, int
- thumbnail, (file FK)
- creator, (user FK)
- show_creator, boolean (name appears in poll?)
- followers, ManyToManyFieid to User
- pub_date, datetime
- vote_start, datetime
- vote_end, datetime
- show_vote, choice (after vote, after end date, never)
- min_selection, int
- max_selection, int
- has_max_vote_count, boolean
- max_vote_count, int
- allow_custom, boolean (allow custom choice)
- choices, see Choice table
- attachments, see Attachment table

## Choice

- question (FK)
- choice_text, string (200 max)
- vote_count, int (derived, read-only)

## Vote

- question (FK)
- timestamp, datatime
- is_custom, boolean (is a custom choice?)
- choice (FK, optional)
- custom choice text, string (200 max, optional)

## Attachment

- question (FK)
- file (FK)


# Data template

## User List Page

- name (sort)
- group (sort)
- search
    - name
- filter
    - group (list)

## User Detail/Edit Page

- name (text)
- email (text)
- group (radio, default/subscriber/super admin)
- subscription start date (date, subscriber only)
- subscription expire date (date, subscriber only)
- followed question list (select existing from list)

## Question List Page

- question text (sort)
- date published (sort)
- vote period (sort)
- vote count (sort)
- vote list (link to new page)
- follower count (sort)
- search
    - question text
- filter
    - time range (datetime range)
    - vote count range (int range)

## Question Detail/Edit Page

- title image (image)
- question text (text)
- attachments (file)
- date published (datetime)
- vote period (datetime range)
- show vote (dropdown, after vote/after end date/never)
- is allow custom (toggle)
- has max vote (radio)
- max vote (number, hidden if unlimited)
- selection count restriction (radio, single/exact/range/unlimited)
- min/max/exact selections (numbers, hidden if single/unlimited)
- choice list (includes read-only vote count, optional custom choices aggregated count)
- follower list (dropdown search)

## Vote List Page

- question text
- vote list
    - timestamp (datetime, sort)
    - choice text (sort)
- filter 
    - choice (checkbox)
    - time range (datetime range)
