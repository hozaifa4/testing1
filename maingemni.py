# telemain.py

# Importing necessary libraries
import logging
import os # Added for environment variables
import sys # Added for exiting on missing env vars
from telethon import TelegramClient, events

# --- Configuration Data (Load from Environment Variables) ---

# --- 1. Your Telegram API Credentials ---
# Set these as environment variables on your server.
api_id_str = os.environ.get('26469046')
api_hash = os.environ.get(' aace933a67363959330ededd42977eb6 ')

# --- 2. Your Phone Number ---
# Set this as an environment variable on your server.
your_phone_number = os.environ.get('+8801875575437')

# --- 3. Source and Destination Channel IDs ---
# Set these as environment variables on your server.
source_channel_id_str = os.environ.get('-1002539468107')
destination_channel_id_str = os.environ.get('-1002695323353')

# --- 4. Session file name ---
# Set this as an environment variable or use a default.
session_file_name = os.environ.get('SESSION_FILE_NAME', 'my_channel_copier_session')

# --- 5. Keywords to filter ---
# Set this as a comma-separated string in an environment variable.
keywords_env = os.environ.get('KEYWORDS_TO_FILTER', "buy,sell") # Default if not set
KEYWORDS_TO_FILTER = [k.strip().lower() for k in keywords_env.split(',')]

# --- Validate essential configuration ---
missing_vars = []
if not api_id_str: missing_vars.append("TELEGRAM_API_ID")
if not api_hash: missing_vars.append("TELEGRAM_API_HASH")
if not your_phone_number: missing_vars.append("TELEGRAM_PHONE_NUMBER")
if not source_channel_id_str: missing_vars.append("SOURCE_CHANNEL_ID")
if not destination_channel_id_str: missing_vars.append("DESTINATION_CHANNEL_ID")

if missing_vars:
    print(f"Error: The following environment variables are not set: {', '.join(missing_vars)}")
    print("Please set them before running the script.")
    sys.exit(1)

# Convert numeric IDs to integers, with error handling
try:
    api_id = int(api_id_str)
    source_channel_id = int(source_channel_id_str)
    destination_channel_id = int(destination_channel_id_str)
except ValueError as e:
    print(f"Error: One of the ID environment variables is not a valid integer: {e}")
    sys.exit(1)

# --- End of Configuration Data ---


# Optional: Logging Configuration
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO) # Change to logging.DEBUG for more detailed logs

# Creating Telegram Client using session name from config
client = TelegramClient(session_file_name, api_id, api_hash)

# Script starting message
print("Python script is starting...")
print(f"Attempting to use session file: {session_file_name}")
print(f"Source Channel ID: {source_channel_id}")
print(f"Destination Channel ID: {destination_channel_id}")
print(f"Filtering for keywords: {KEYWORDS_TO_FILTER} and the first '$'-prefixed word.")
print("Output mode: Extracted 'action_word $first_dollar_word'")

# Event handler for new messages
@client.on(events.NewMessage(chats=source_channel_id))
async def handle_new_message(event):
    message = event.message
    matched_action_word = None
    first_dollar_word = None

    if message.text:  # Only process messages with text content
        message_text_original = message.text # Keep original text for extracting $-word case
        message_text_lower = message_text_original.lower()  # For case-insensitive keyword matching

        # 1. Check for action keywords
        for keyword_to_check in KEYWORDS_TO_FILTER:
            if keyword_to_check in message_text_lower:
                matched_action_word = keyword_to_check
                break
        
        if matched_action_word:
            # 2. If action keyword found, search for the first $-prefixed word
            words_in_message = message_text_original.split() 
            for word in words_in_message:
                if word.startswith('$') and len(word) > 1:
                    first_dollar_word = word
                    break 
            
            if first_dollar_word:
                output_message = f"{matched_action_word} {first_dollar_word}"
                
                print(f"Message ID {message.id}: Action='{matched_action_word}', DollarWord='{first_dollar_word}'. Sending: '{output_message}'")
                try:
                    await client.send_message(
                        destination_channel_id,
                        output_message,
                        link_preview=False
                    )
                    print(f"Condensed message from ID {message.id} sent to channel {destination_channel_id}.")
                except Exception as e:
                    print(f"Error sending condensed message from ID {message.id}: {e}")
            else:
                print(f"Message ID {message.id} contains action word '{matched_action_word}' but no $-prefixed word. Skipped.")
        else:
            print(f"Message ID {message.id} does not contain configured keywords. Skipped.")
    else:
        print(f"Message ID {message.id} has no text content. Skipped.")

# Main function
async def main():
    try:
        await client.start(phone=lambda: your_phone_number)
            
    except Exception as e:
        print(f"Could not connect or authorize with Telegram: {e}")
        print("Ensure API credentials and phone number are correct in your environment variables.")
        print("If it's the first run or the session file is invalid, interactive input for the login code might be required.")
        return

    print("Telegram client connected and authorized successfully.")
    print(f"Waiting for new messages in source channel ({source_channel_id}) for processing...")
    try:
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Client disconnected with error: {e}")
    finally:
        print("Attempting to gracefully disconnect client...")
        await client.disconnect() # Gracefully disconnect client

# Script execution
if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped by Ctrl+C.")
    except Exception as e:
        print(f"An unexpected error occurred in the main execution block: {e}")
    finally:
        print("Script execution finished.")