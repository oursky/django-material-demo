# Data Model

## Question

- title image, image/byte
- question text, string (200 max)
- choices, see Choice table
- is allow custom, boolean (allow custom choice)
- date published, datetime
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
