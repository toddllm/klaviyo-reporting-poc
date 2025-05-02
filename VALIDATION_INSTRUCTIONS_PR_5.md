# Validation Instructions for PR 5: Campaign Creation Script

Before merging this PR, the validation dev should verify the following:

## 1. Test Dry-Run Mode

Run the script in dry-run mode to verify it shows the correct API requests that would be made:

```bash
python create_send_campaign.py --dry-run
```

Verify that:
- It shows the campaign creation payload
- It shows the template assignment payload
- No actual API calls are made
- The script completes successfully

## 2. Verify API Request Structure

Examine the dry-run output and verify that:
- The campaign creation payload includes the correct audience structure
- The template assignment uses the correct relationships format
- The send job payload is properly formatted

## 3. Test Propagation Check

Run the script with a small test and verify that it properly waits for the message to be ready:

```bash
python create_send_campaign.py --name "Test Campaign $(date +%s)" --dry-run
```

Then check the code to verify:
- It includes `time.sleep(10)` after template assignment
- It polls for `message.status == 'ready'` before sending
- It uses exponential backoff for polling

## 4. Verify Campaign Status Check

Examine the code to ensure it properly fetches the campaign message status:

```bash
grep -A 10 "check_message_status" create_send_campaign.py
```

Verify that:
- The function correctly fetches the message status
- It properly handles error conditions
- The status check is performed before sending the campaign

## 5. Run Unit Tests

Run the unit tests to verify the functionality:

```bash
python -m pytest tests/test_campaign_creation.py -v
```

All tests should pass, confirming that:
- Campaign creation works correctly
- Template assignment works correctly
- Message status checking works correctly
- Campaign sending works correctly

The PR should only be merged when all these validation steps pass successfully.
