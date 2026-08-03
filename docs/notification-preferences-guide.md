# Notification Preferences Guide

## Model

`NotificationPreference` has:
- `channel` — `in_app`, `email`, `push`, `sms`, `webhook`
- `category` — `*` for all, or a specific category
- `enabled`
- `frequency` — `realtime`, `daily`, `weekly`
- `digest`
- `quiet_hours_start` / `quiet_hours_end` — `HH:MM`
- `language`

## Matching

`PreferenceService.is_enabled(user_id, channel, category)` checks the most specific preference for `category` (or `*`) and `channel`.

## Defaults

If no preference exists, the default is `enabled = True`.

## API

- `GET /api/v1/communications/preferences`
- `POST /api/v1/communications/preferences`
