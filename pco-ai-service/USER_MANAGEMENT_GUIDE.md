# 👤 User Management Guide - Interactive Chat

This guide explains how to add and manage users through the PCO AI Interactive Chat.

## Quick Start

### Launch Interactive Chat

```bash
cd pco-api-wrapper/pco-ai-service
python interactive_chat.py
```

Or use the batch file:
```bash
cd pco-api-wrapper/pco-ai-service
chat.bat
```

## Adding a New Person

### Method 1: Using the /addperson Command (Recommended)

1. **Start the interactive chat**
2. **Type `/addperson`**
3. **Follow the prompts:**

```
👤 Add New Person to PCO
======================================================================
Please provide the following information:
----------------------------------------------------------------------

First Name (required): John
Last Name (required): Doe
Gender (Male/Female/optional): Male
Birthdate (YYYY-MM-DD/optional): 1990-05-15
Email (optional): john.doe@example.com

----------------------------------------------------------------------
📋 Review Information:
----------------------------------------------------------------------
Name: John Doe
Gender: Male
Birthdate: 1990-05-15
Email: john.doe@example.com
----------------------------------------------------------------------

Add this person? (yes/no): yes

⏳ Adding person to PCO...

======================================================================
✅ Person Added Successfully!
======================================================================

Person ID: 12345678
Name: John Doe
Email: john.doe@example.com (added)

======================================================================
```

### Method 2: Ask the AI to Add a Person

You can also ask the AI in natural language:

```
You: Can you help me add a new member named Sarah Smith?
AI: I can guide you through adding Sarah Smith. Let me help you with that...
```

Then use `/addperson` to complete the process.

## Required Information

### Mandatory Fields
- **First Name** - Person's first name
- **Last Name** - Person's last name

### Optional Fields
- **Gender** - Male, Female, or leave blank
- **Birthdate** - Format: YYYY-MM-DD (e.g., 1990-05-15)
- **Email** - Email address (will be added as "Home" location)

## Features

### ✅ What the Command Does

1. **Validates Input** - Ensures required fields are provided
2. **Shows Preview** - Displays all information before submitting
3. **Confirms Action** - Asks for confirmation before adding
4. **Creates Person** - Adds the person to Planning Center Online
5. **Adds Email** - Automatically adds email if provided
6. **Shows Result** - Displays the new person's ID and details

### 🔒 Safety Features

- **Confirmation Required** - Must type "yes" to proceed
- **Cancel Anytime** - Type "no" to cancel
- **Error Handling** - Clear error messages if something goes wrong
- **Connection Check** - Verifies API is available

## Examples

### Example 1: Minimal Information
```
First Name (required): Jane
Last Name (required): Smith
Gender (Male/Female/optional): [press Enter]
Birthdate (YYYY-MM-DD/optional): [press Enter]
Email (optional): [press Enter]

Add this person? (yes/no): yes
```

### Example 2: Complete Information
```
First Name (required): Michael
Last Name (required): Johnson
Gender (Male/Female/optional): Male
Birthdate (YYYY-MM-DD/optional): 1985-03-20
Email (optional): michael.j@email.com

Add this person? (yes/no): yes
```

### Example 3: Cancel Operation
```
First Name (required): Test
Last Name (required): User
Gender (Male/Female/optional): 
Birthdate (YYYY-MM-DD/optional): 
Email (optional): 

Add this person? (yes/no): no
❌ Cancelled
```

## Troubleshooting

### Error: "Cannot connect to PCO API"

**Problem:** The PCO API Wrapper is not running

**Solution:**
```bash
# Start the API wrapper
cd pco-api-wrapper
python src/app.py

# Or use the startup script
start-all-services.bat
```

### Error: "first_name and last_name are required"

**Problem:** Missing required fields

**Solution:** Ensure you provide both first and last name

### Error: "Invalid birthdate format"

**Problem:** Birthdate not in correct format

**Solution:** Use YYYY-MM-DD format (e.g., 1990-05-15)

### Person Added but Email Failed

**Problem:** Person created but email couldn't be added

**Solution:** 
1. Note the Person ID from the success message
2. Add email manually later using the API or PCO interface

## All Available Commands

| Command | Description |
|---------|-------------|
| `/addperson` | Add a new person to PCO |
| `/help` | Show all available commands |
| `/new` | Start a new chat session |
| `/context` | Show conversation history |
| `/clear` | Clear conversation history |
| `/quit` or `/exit` | Exit the chat |

## Integration with AI Chat

The `/addperson` command works seamlessly with the AI chat:

1. **Ask the AI** about adding members
2. **Use `/addperson`** to actually add them
3. **Continue chatting** with the AI about the new member

Example workflow:
```
You: I need to add a new volunteer
AI: I can help you with that. Use the /addperson command to add them...

You: /addperson
[Follow the prompts to add the person]

You: Great! Can you show me all volunteers now?
AI: [Fetches and displays volunteer list]
```

## API Endpoints Used

The `/addperson` command uses these API endpoints:

1. **Create Person:**
   ```
   POST http://localhost:5000/api/people
   ```

2. **Add Email (if provided):**
   ```
   POST http://localhost:5000/api/people/{person_id}/emails
   ```

## Best Practices

### ✅ Do's
- ✅ Verify information before confirming
- ✅ Use proper date format (YYYY-MM-DD)
- ✅ Provide email when available
- ✅ Check the success message for Person ID

### ❌ Don'ts
- ❌ Don't add duplicate people (check first)
- ❌ Don't use invalid email formats
- ❌ Don't skip required fields
- ❌ Don't forget to note the Person ID

## Advanced Usage

### Batch Adding Multiple People

For adding multiple people, you can:

1. Use `/addperson` multiple times
2. Or create a script using the API directly

### Adding Additional Information Later

After adding a person, you can add more details:

1. **Note the Person ID** from the success message
2. **Use the API** to add phone numbers, addresses, etc.
3. **Or use PCO interface** for complex updates

## Support

For issues or questions:
- Check the main README.md
- Review TROUBLESHOOTING.md
- Check API documentation at http://localhost:5000 when running

## Related Documentation

- [Interactive Chat Guide](README.md)
- [PCO API Wrapper Documentation](../README.md)
- [API Endpoints](../QUICKSTART.md)