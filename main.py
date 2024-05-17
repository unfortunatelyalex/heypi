import os
import logging
import asyncio
import nextcord
import aiosqlite
from dotenv import load_dotenv
from nextcord.ext import commands
from logging.handlers import RotatingFileHandler

cogs = [
    'cogs.about',
    'cogs.admin',
    'cogs.chat',
    'cogs.cookieman',
    'cogs.discord',
    'cogs.events',
    'cogs.faq',
    'cogs.help',
    'cogs.privacy',
    ]


# CONFIGURE LOG
logger_info = logging.getLogger("INFO")
logger_info.setLevel(logging.INFO)

logger_error = logging.getLogger("ERROR")
logger_error.setLevel(logging.ERROR)

logger_debug = logging.getLogger("DEBUG")
logger_debug.setLevel(logging.DEBUG)

# Clear any existing handlers to avoid duplicates (optional)
logger_info.handlers.clear()
logger_error.handlers.clear()
logger_debug.handlers.clear()

# Create handlers for info and error logs
info_handler = RotatingFileHandler('info.log', maxBytes=100000, backupCount=3)
error_handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=3)
debug_handler = RotatingFileHandler('debug.log', maxBytes=100000, backupCount=3)

# Set the log level for each handler
info_handler.setLevel(logging.INFO)
error_handler.setLevel(logging.ERROR)
debug_handler.setLevel(logging.DEBUG)

# Create formatters and add them to the handlers
info_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%b-%d %H:%M:%S')
error_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%b-%d %H:%M:%S')
debug_formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', datefmt='%Y-%b-%d %H:%M:%S')
info_handler.setFormatter(info_formatter)
error_handler.setFormatter(error_formatter)
debug_handler.setFormatter(debug_formatter)

# Add the handlers to the respective loggers
logger_info.addHandler(info_handler)
logger_error.addHandler(error_handler)
logger_debug.addHandler(debug_handler)

load_dotenv()


class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.init_db())

    async def init_db(self):
        self.conn = await aiosqlite.connect(self.db_file)
        await self.create_table()

    async def create_table(self):
        try:
            cursor = await self.conn.cursor()
            await cursor.execute("""CREATE TABLE IF NOT EXISTS cookies (
                                        id INTEGER PRIMARY KEY,
                                        user_id TEXT NOT NULL,
                                        host_session TEXT NOT NULL
                                    );""")
            await self.conn.commit()
        except Exception as e:
            logger_error.error(f'{e}')

    async def load_cookies(self, user_id):
        cursor = await self.conn.cursor()
        await cursor.execute("SELECT host_session FROM cookies WHERE user_id=?", (user_id,))

        rows = await cursor.fetchall()
        
        if rows:
            return {
                '__Host-session': rows[0][0]
            }
        else:
            return None

    async def save_cookies(self, host_session, user_id):
        cursor = await self.conn.cursor()
        try:
            await cursor.execute("SELECT 1 FROM Cookies WHERE user_id=?", (user_id,))
            exists = await cursor.fetchone() is not None

            if exists:
                await cursor.execute("UPDATE Cookies SET host_session = ? WHERE user_id = ?", (host_session, user_id))
            else:
                await cursor.execute("INSERT INTO Cookies (user_id, host_session) VALUES(?, ?)", (user_id, host_session))
            
            await self.conn.commit()
        except Exception as e:
            logger_error.error(f'{e}')

    async def delete_cookies(self, user_id):
        cursor = await self.conn.cursor()
        try:
            await cursor.execute("DELETE FROM Cookies WHERE user_id=?", (user_id,))
            await self.conn.commit()
        except Exception as e:
            logger_error.error(f'{e}')

    async def close(self):
        await self.conn.close()




async def initialize_database():
    conn = await aiosqlite.connect('message_history.db')
    cursor = await conn.cursor()
    await cursor.execute('CREATE TABLE IF NOT EXISTS message_history (user_id TEXT PRIMARY KEY)')
    await conn.commit()
    await conn.close()

async def check_user_in_database(user_id):
    conn = await aiosqlite.connect('message_history.db')
    cursor = await conn.cursor()
    await cursor.execute('SELECT user_id FROM message_history WHERE user_id=?', (user_id,))
    result = await cursor.fetchone()
    await conn.close()
    return result is not None

async def add_user_to_database(user_id):
    conn = await aiosqlite.connect('message_history.db')
    cursor = await conn.cursor()
    await cursor.execute('INSERT INTO message_history (user_id) VALUES (?)', (user_id,))
    await conn.commit()
    await conn.close()



intents = nextcord.Intents.default()
#intents.message_content = True

embed_footer = 'made with 💛 by alexdot but all credits go to Inflection AI'
bot = commands.AutoShardedBot(
    shard_count=10,
    owner_id="399668151475765258",
    intents=intents
    )
bot.remove_command('help')
db = Database(f'{os.getenv("database_path")}')







@bot.event
async def on_ready():
    print('-------------------------------------------')
    print(f"          Logged in as {bot.user} ")
    print(f"       User-ID = {bot.user.id}")
    print(f"             Version = {nextcord.__version__}")
    print('-------------------------------------------')
    custom = nextcord.CustomActivity(name="Chat with me!")
    await bot.change_presence(activity=custom, status=nextcord.Status.online)
    try:
        await initialize_database()
    except Exception as e:
        logger_error.error(f"Error: {e}")
        print(f"Error: {e}")



for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loaded {filename}")
print('-------------------------------------------')
print(f"               Loaded {len(bot.cogs)} cogs")




bot.run(os.getenv("TOKEN"))
