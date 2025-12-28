# Telegram Bot Template

Production-ready, async Telegram bot starter built on `python-telegram-bot`. It provides a clean project structure, automatic command discovery, permission decorators, cooldown scheduling with persistence, graceful shutdown/restart, simple i18n, and an opinionated dev→prod publishing flow.

This template helps you ship a Telegram bot fast while keeping maintainability and operational safety in mind.

## Features
- **Auto command discovery:** Functions ending with `_command` are auto-registered as `/commands`; `_inline` handlers register `CallbackQueryHandler`s.
- **Permissions & gating:** `require_admin`, `require_registered`, `require_private`, plus global dev-mode user gating.
- **Cooldown scheduler:** Schedule deferred actions with persistence across restarts using JSON + `dill`.
- **Graceful lifecycle:** Clean shutdown saves cooldowns, language preferences, reader caches, and closes the DB.
- **i18n basics:** Pluggable language files with `get_text()` and `/setlang <code>`.
- **Structured project:** Clear `dev/` runtime, `prod/` deploy target, and `publish.sh` for safe syncing with backups.
- **Batteries included:** Venv bootstrap, dependency check/install, command logging, and database scaffolding (Peewee).

## Requirements
- Python 3.10+ (recommended for `python-telegram-bot` v20+)
- A Telegram bot token from BotFather
- Linux/macOS shell to use the provided scripts (Windows works via WSL/PowerShell with minor adjustments)

## Quick Start (Development)
1. Create a bot with BotFather and copy the token.
2. Create a `.env` file inside `dev/` with at least:

```env
BOT_TOKEN=123456789:ABCDEF_your_token_here
BOT_MODE=dev
# Optional: comma-separated admin IDs
ADMINS=111111111,222222222
# Optional: allowed users (dev gating)
ALLOWED_USERS=333333333,444444444
```

3. Start the bot (script creates/activates a venv and installs deps on first run):

```bash
bash dev/start.sh
```

The dev runner restarts automatically when `/reload` is issued by an admin.

## How It Works
- **Entry point:** [dev/bot.py](dev/bot.py) builds the `Application`, auto-loads commands, starts polling, and runs background tasks (e.g., cooldown watcher).
- **Config:** [dev/config/config.py](dev/config/config.py) loads env vars (`BOT_TOKEN`, `BOT_MODE`, `ADMINS`, `ALLOWED_USERS`) via `dotenv` and manages dev-only `allowed_users.json`.
- **Permissions:** [dev/utils/permissions.py](dev/utils/permissions.py) provides decorators and a `global_restrict()` wrapper applied to all handlers.
- **Cooldowns:** [dev/utils/cooldown.py](dev/utils/cooldown.py) saves state to `data/status/cooldowns.json` and `data/status/callbacks.pkl` and processes due callbacks.
- **Language texts:** [dev/modules/texts](dev/modules/texts) contains language modules; `/setlang <code>` updates per-user preference.
- **Command logging:** [dev/utils/command_logger.py](dev/utils/command_logger.py) logs every slash command execution.
- **Database hooks:** `initialize_database()` and `close_db_connection()` are called at startup/shutdown (see `database/`).

## Built-in Commands
- `/start`: Sends a greeting using the active language texts.
- `/setlang <code>`: Sets language (e.g., `en`, `it`).
- `/reload`: Admin-only; schedules a safe restart via cooldown callback and signals the dev runner to reload.

See implementations in:
- [dev/modules/commands/basic/basic.py](dev/modules/commands/basic/basic.py)
- [dev/modules/commands/lang/lang.py](dev/modules/commands/lang/lang.py)

## Adding a New Command
1. Create a Python module under `dev/modules/commands/<group>/` (e.g., `dev/modules/commands/tools/tools.py`).
2. Define an async function ending with `_command`:

```python
from utils.permissions import require_private
from modules.texts import get_text

@require_private()
async def ping_command(update, context):
		await update.message.reply_text(get_text(key="PING", update=update))
```

3. Optional: add inline handlers by ending the function name with `_inline` and parsing `update.callback_query.data`.

The loader in [dev/bot.py](dev/bot.py) auto-discovers and registers these handlers. All handlers are wrapped with `global_restrict()` so dev-mode gating and bans apply consistently.

## Permissions & Dev Gating
- **Admins:** Set in `.env` via `ADMINS`. Use `@require_admin()` to restrict commands.
- **Registered users:** Implement `utils.data_reading.get_data("registered", user_id)` and use `@require_registered()`.
- **Private-only:** Use `@require_private()` for commands that must run in private chats.
- **Global dev gating:** In `BOT_MODE=dev`, only `ADMINS` and `ALLOWED_USERS` may use the bot. The list is persisted to [dev/config/allowed_users.json](dev/config/allowed_users.json) and can be augmented via `ALLOWED_USERS` env.

## Cooldowns & Deferred Actions
Schedule actions to run later and persist them across restarts:

```python
from utils.cooldown import add_cooldown
from utils.callback import Callback

async def notify_complete(**kwargs):
		bot = kwargs['bot']
		chat = kwargs['chat']
		await bot.send_message(chat_id=chat['id'], text="Done!")

# e.g., inside a command
cb = Callback(async_func=notify_complete, chat=update.message.chat, user=update.message.from_user)
add_cooldown(update.effective_user.id, "NOTIFY", 10, cb)  # runs in ~10s
```

`Callback` auto-serializes `User`/`Chat` to dicts; the bot instance is injected at runtime by the watcher.

## Internationalization (i18n)
- Add a file under [dev/modules/texts](dev/modules/texts) (e.g., `texts_fr.py`) defining `LANG_CODE`, `LANG_FULLNAME`, and string keys.
- Ensure keys used by commands exist (e.g., `START`, `LINGUA_IMPOSTATA`, `LINGUA_NON_IMPOSTATA`).
- Users can switch language via `/setlang <code>`.

Example language module:

```python
LANG_FULLNAME = "ENGLISH"
LANG_CODE = "en"
START = "Hello {{username}}!"
```

## Configuration Reference
- `BOT_TOKEN`: Telegram bot token from BotFather.
- `BOT_MODE`: `dev` or `prod`. In `dev`, global gating applies; in `prod`, all users can interact unless otherwise restricted.
- `ADMINS`: Comma-separated Telegram user IDs with admin privileges.
- `ALLOWED_USERS`: Comma-separated user IDs allowed to interact in `dev`.

## Project Structure
```
dev/
	bot.py              # app init, loader, polling, tasks
	start.sh            # venv bootstrap + dev runner with auto-reload
	requirements.txt    # core dependencies
	config/
		config.py         # env, mode, admins, allowed users
		allowed_users.json# persisted allowed users (dev)
	modules/
		commands/         # command groups and handlers (*_command, *_inline)
		texts/            # language modules and extras
	utils/
		permissions.py    # decorators + global restrict wrapper
		cooldown.py       # scheduler with persistence
		callback.py       # serializable async callback wrapper
		command_logger.py # simple logging of slash commands
	data/               # reader caches, status data (cooldowns)
	database/           # DB initialization/teardown hooks (Peewee)
prod/
	config/             # target for published code
backups/              # timestamped prod backups created by publish.sh
publish.sh            # safe deploy dev → prod with backups
```

## Development Tips
- Use `/reload` to safely restart the bot while preserving cooldowns and preferences.
- Add new commands under `modules/commands/` using the naming convention; they’re auto-registered at startup.
- Keep long-running tasks off the main thread; use asyncio and background tasks as shown by `cooldown_watcher()`.

## Publishing to Production
This project includes a simple, safe deploy script:

```bash
# From the project root
bash publish.sh
```

What it does:
- Creates a timestamped backup of `prod/` under `backups/`.
- Syncs `dev/` to `prod/` with `.rsyncignore` exclusions.
- Keeps only the last N backups (default 5).

In production, set `BOT_MODE=prod` and manage environment variables and process supervision (e.g., `systemd`, `pm2`, or a custom script) according to your hosting setup.

## Dependencies
See [dev/requirements.txt](dev/requirements.txt). On first run, `dev/start.sh` creates a venv and installs missing packages.

```text
python-telegram-bot
dill
emoji
peewee
dotenv
```

## Troubleshooting
- "Unauthorized" in dev: Add your user ID to `ADMINS` or `ALLOWED_USERS`, or use `/reload` after updating `.env`.
- Token issues: Confirm `BOT_TOKEN` is present in `dev/.env` and the bot is not paused in BotFather.
- No commands loaded: Ensure your functions are `async` and end with `_command`. Modules must be inside `dev/modules/commands/`.
- Inline not firing: Functions must end with `_inline`; check `CallbackQueryHandler` patterns and `query.data` formatting.
- Persistence errors: Delete `data/status/*` if formats changed during development; they’ll be recreated.

## Acknowledgements
- Built on the excellent [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot).

