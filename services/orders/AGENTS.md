# orders

- `repository.py` is the only module that runs SQL. Handlers in `app.py` call it and map its exceptions to HTTP statuses.
- A status changes only through `repository.move`, which checks `TRANSITIONS` and updates with the old status in the condition.
- Request and response shapes live in `models.py`. After a change there, run `make contract`.
