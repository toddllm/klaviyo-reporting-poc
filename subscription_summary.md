# Klaviyo Subscription POC Summary

**Date:** 2025-05-06

## Objective
We are building a proof-of-concept to subscribe mock user profiles to a Klaviyo list via the Klaviyo API. Once subscribed, these profiles should appear in the Klaviyo dashboard and be available for sending test campaigns and collecting engagement metrics.

## Code Components
- **`config.py`**: Loads `.env` values, including `KLAVIYO_API_KEY` and `AUDIENCE_ID`.
- **`seed_profiles.py`** (`create_and_subscribe_profiles`): Flattens profile data and calls the JSON:API endpoint `/api/lists/{AUDIENCE_ID}/relationships/profiles/` to subscribe profiles in bulk.
- **`subscribe_mock_profiles.py`** (`subscribe_mock_profiles.py`): Generates random profiles and individually subscribes them using the list-members endpoint (`/api/v1/list/{AUDIENCE_ID}/members`).

## Attempts & Changes
1. **V2 JSON:API Relationship**: Pointed `seed_profiles.py` at `/api/lists/{AUDIENCE_ID}/relationships/profiles/` with JSON:API payload.
2. **V1 List-Members**: Switched both scripts to `/api/v1/list/{AUDIENCE_ID}/members` with `api_key` param.
3. **Header Adjustments**: Tried moving API key into `Authorization` header and adding `Revision` for versioning.

## Errors Encountered
- **410 Gone** (`/api/v1/list/YdSN6t/members?api_key=…`): Indicates the list ID is invalid or removed.
- **404 Not Found** (`/api/lists/YdSN6t/relationships/profiles/`): Endpoint exists, but the list ID `YdSN6t` is not found in the account.

## Root Cause
The configured `AUDIENCE_ID` (`YdSN6t`) does not match an active list in the Klaviyo account.

## Next Steps
1. Log into the Klaviyo dashboard and copy the correct List ID.
2. Update `AUDIENCE_ID` in `.env` or `config.py`.
3. Re-run the subscription scripts:
   ```bash
   python subscribe_mock_profiles.py
   python subscribe_all.py
   ```
4. Verify that the new profiles appear under the specified list in Klaviyo.

## Success Criteria
- Subscription script completes without HTTP errors.
- Profiles show up in the Klaviyo list dashboard as “Subscribed.”
- Test campaigns can be sent to these profiles and engagement metrics (opens, clicks, etc.) are recorded.
