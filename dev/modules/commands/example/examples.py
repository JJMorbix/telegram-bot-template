from modules.texts import get_text
from utils.callback import Callback
from utils.permissions import require_private, require_registered

@require_private()
async def example1_command(update, context):
    print("LOL")
    msg = "You are using <b>example1</b> command in private chat!"
    # NOT STANDARD WAY TO GET TEXTS, JUST FOR DEMO PURPOSES
    
    await update.message.reply_text(msg, parse_mode="HTML")

#@require_registered()
# For info on why this check is commented, see commands/basic/basic.py on the start command
async def example2_command(update, context):
    msg = "You are using <b>example2</b> command as a registered user!"
    # NOT STANDARD WAY TO GET TEXTS, JUST FOR DEMO PURPOSES
    
    await update.message.reply_text(msg, parse_mode="HTML")

async def example3_command(update, context):
    from utils.cooldown import is_in_cooldown
    if is_in_cooldown(update.message.from_user.id, "EXAMPLE"):
        msg = "You are in cooldown for this command. Please wait before using it again."
        await update.message.reply_text(msg, parse_mode="HTML")
        return
    msg = "You are using <b>example3</b> command to start a 5 sec timer!"
    # NOT STANDARD WAY TO GET TEXTS, JUST FOR DEMO PURPOSES

    user_id = update.message.from_user.id
    from utils.callback import Callback
    cb = Callback(
        async_func=example3_complete,
        chat=update.message.chat,
        message_id=update.message.message_id,
        user=update.message.from_user,
        action_id="EXAMPLE",
        other_data="some_data",
        another_field=12345
    )

    from utils.cooldown import add_cooldown
    add_cooldown(update.message.from_user.id, "EXAMPLE", 5, cb)
    
    await update.message.reply_text(msg, parse_mode="HTML")
    
async def example3_complete(**kwargs):
    bot = kwargs['bot']
    user = kwargs['user']
    other_data = kwargs['other_data']
    another_field = kwargs['another_field']
    
    await bot.send_message(chat_id=kwargs['chat']['id'], text=f"Your 5 seconds timer is complete! Your data was: {other_data}, {another_field}", reply_to_message_id=kwargs['message_id'], parse_mode="HTML")

async def example4_command(update, context):
    # This command shows the intended use of strings
    msg = get_text("ESEMPIO", update=update)
    await update.message.reply_text(msg, parse_mode="HTML")