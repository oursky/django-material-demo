# Data Model

## Question

- title image, image/byte
- question text, string (200 max)
- choices, see Choice table
- is allow custom, boolean (allow custom choice)
- min selections, int
- max selections, int
- vote start date, datetime
- vote end date, datetime
- show vote, enum (after vote, after end date, never)
- max vote, int
- attachments, see Attachment table

## Choice

- question (FK)
- choice text, string (200 max)
- votes, int (derived, read-only)

## Vote

- question (FK)
- timestamp, datatime
- is custom, boolean (is a custom choice?)
- choice (FK, optional)
- custom choice text, string (200 max, optional)

## Attachment
- question (FK)
- file, file/byte


# Data template

## Question List Page

- question text
- vote period
- vote count
- vote list (link to new page)
- search
    - question text
- filter
    - time range (datetime range)
    - vote count range (int range)

## Question Detail/Edit Page

- title image (image)
- question text (text)
- attachments (file)
- vote period (datetime range)
- show vote (dropdown, after vote/after end date/never)
- is allow custom (toggle)
- has max vote (radio)
- max vote (number, hidden if unlimited)
- selection count restriction (radio, single/exact/range/unlimited)
- min/max/exact selections (numbers, hidden if single/unlimited)
- choice list (includes read-only vote count, optional custom choices aggregated count)

## Vote List Page

- question text
- vote list
    - timestamp (datetime)
    - choice text (text)
- filter 
    - choice (checkbox)
    - time range (datetime range)
