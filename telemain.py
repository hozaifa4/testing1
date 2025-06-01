# telegram_script.py (Single file combining config and main logic)

# Importing necessary libraries
from telethon import TelegramClient, events
import logging

# --- Configuration Data (Previously in config.py) ---

# --- 1. Your Telegram API Credentials ---
# You obtained this information from my.telegram.org.
# Set the following values in this script file on your own computer.
api_id = 26469046  # <--- Enter your API ID here (e.g., 26469046)
api_hash = 'aace933a67363959330ededd42977eb6' # <--- Enter your API Hash here (e.g., 'aace933a67363959330ededd42977eb6')

# --- 2. Your Phone Number ---
# The phone number of the Telegram account whose API ID & Hash you are using.
# Required for the first login and session authentication.
your_phone_number = '+8801875575437'  # <--- Enter your phone number here in international format (e.g., '+8801875575437')

# --- 3. Source and Destination Channel IDs ---
# These are the numeric IDs for your channels.
# Your previously provided channel IDs are used here.
source_channel_id = -1002539468107        # Source channel ID
destination_channel_id = -1002695323353  # Destination channel ID (your channel)

# --- 4. Session file name ---
# The script will create a file with this name to store login session.
session_file_name = 'my_channel_copier_session'

# --- 5. Keywords to filter ---
# Define your keywords here (lowercase for consistent checking)
KEYWORDS_TO_FILTER = ["buy", "sell"]

# --- End of Configuration Data ---


# Optional: Logging Configuration
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO) # Change to logging.DEBUG for more detailed logs if needed

# Creating Telegram Client using session name from config
client = TelegramClient(session_file_name, api_id, api_hash)

# Script starting message
print("Python script is starting...")
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

        # 1. Check for action keywords ("buy" or "sell")
        for keyword_to_check in KEYWORDS_TO_FILTER:
            if keyword_to_check in message_text_lower:
                matched_action_word = keyword_to_check  # Store the matched keyword (already lowercase)
                break
        
        if matched_action_word:
            # 2. If action keyword found, search for the first $-prefixed word
            # We split the original message text to preserve the case of the $-prefixed word
            words_in_message = message_text_original.split() 
            for word in words_in_message:
                if word.startswith('$') and len(word) > 1: # Word starts with $ and has characters after $
                    first_dollar_word = word  # Take the first one found, preserving its original case
                    break 
            
            if first_dollar_word:
                # Both action word and a dollar word are found, create and send new message
                output_message = f"{matched_action_word} {first_dollar_word}"
                
                print(f"Message ID {message.id}: Action='{matched_action_word}', DollarWord='{first_dollar_word}'. Sending: '{output_message}'")
                try:
                    await client.send_message(
                        destination_channel_id,
                        output_message,
                        link_preview=False # Set to True if you want link previews for any links in the $-word
                    )
                    print(f"Condensed message from ID {message.id} sent to channel {destination_channel_id}.")
                except Exception as e:
                    print(f"Error sending condensed message from ID {message.id}: {e}")
            else:
                # Action word found, but no $-prefixed word found in the message
                print(f"Message ID {message.id} contains action word '{matched_action_word}' but no $-prefixed word. Skipped.")
        else:
            # No action keyword ("buy" or "sell") found in the message
            print(f"Message ID {message.id} does not contain keywords 'buy' or 'sell'. Skipped.")
    else:
        # Message has no text content
        print(f"Message ID {message.id} has no text content. Skipped.")

# Main function
async def main():
    # Attempt to connect to Telegram
    try:
        # Using client.start() which handles connect and authorization
        # The phone number is passed directly or via lambda for interactive input if needed
        await client.start(phone=lambda: your_phone_number)
            
    except Exception as e:
        print(f"Could not connect or authorize with Telegram: {e}")
        print("Please ensure your API ID, API Hash, and phone number are correct and you have internet access.")
        return # Exit if connection/authorization fails

    print("Telegram client connected and authorized successfully.")
    print(f"Waiting for new messages in source channel ({source_channel_id}) for processing...")
    try:
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Client disconnected with error: {e}")


# Script execution (Run) part
if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram is being stopped by Ctrl+C...")
    except Exception as e: # Catch any other unexpected errors during script execution
        print(f"An unexpected error occurred in the main execution block: {e}")
    finally:
        # Gracefully disconnect the client
        # Ensure client.disconnect() is awaited if it's an async function and called from an async context
        # For a simple script like this, ensuring it's called is good.
        # However, direct asyncio.run in finally can be problematic if event loop is closed.
        # Telethon's client.disconnect() should ideally be awaited if called from an async func.
        # For simplicity in a script ending this way, a print statement is often sufficient.
        # If client.is_connected():
        #    print("Attempting to disconnect client...")
        #    asyncio.run(client.disconnect()) # This line might cause issues in `finally`
        print("Script execution finished.")