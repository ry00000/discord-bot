from discord.ext import commands

import json, asyncio, aiohttp, time, discord

with open("./config.json", "r") as f:
    config = json.load(f)

description = config["description"]

startup_exts = config["extensions"]["startup"]

prefixes = config["prefixes"]

bot_owners = config["owners"]

wrap = "```py\n{}\n```" # Needed for eval

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*prefixes), 
    description=description, 
    owner_id=190544080164487168, 
    game=discord.Game(name=config["game"]["name"], url=config["game"]["url"], type=config["game"]["status"]))

async def is_owner(ctx):
    return ctx.author.id in bot_owners

@bot.event
async def on_ready():
    print("Bot logged in successfully: {} ({})".format(bot.user.name, bot.user.id))

@bot.command(description="Pong!")
async def ping(ctx):
    """Pong!"""
    before = time.monotonic()
    pong = await ctx.send("...")
    after = time.monotonic()
    ping = (after - before) * 1000
    await pong.edit(content="Pong! {}ms".format(int(ping)))


@bot.command(description="Loads an extension", aliases=["le"])
@commands.check(is_owner)
async def load(ctx, cog_name : str):
    """Loads an extension"""
    try:
        bot.load_extension("extensions."+cog_name)
        print("Loading extension {}".format(cog_name))
    except Exception as e:  # pylint: disable=bare-except
        await ctx.send("```\n{}```".format(e))
        return
    await ctx.send("Loaded extension {}".format(cog_name))
    

@bot.command(description="Unloads an extension", aliases=["ule"])
@commands.check(is_owner)
async def unload(ctx, ename : str):
    """Unloads an extension."""
    try:
        bot.unload_extension("extensions."+ename)
        print("Unloading extension {}".format(ename))
    except Exception as e:  # pylint: disable=bare-except
        await ctx.send("```\n{}```".format(e))
        return
    await ctx.send("Unloaded extension {}".format(ename))

@bot.command(description="Reloads an extension", aliases=["rle", "reloady"])
@commands.check(is_owner)
async def reload(ctx, ename : str):
    """Reloads an extension."""
    try:
        bot.unload_extension("extensions."+ename)
        print("Unloading extension {}".format(ename))
        bot.load_extension("extensions."+ename)
        print("Reloading extension {}".format(ename))
    except Exception as e: # pylint: disable=bare-except
        await ctx.send("```\n{}```".format(e))
        return
    await ctx.send("Reloaded extension {}".format(ename))

@bot.command(description="Stops the bot.", aliases=["quit", "disconnect", "stop"], name="exit")
@commands.check(is_owner)
async def _exit(ctx):
    await ctx.send("Bot shutting down...")
    exit()

@bot.command(description="Evaluates some code. VERY DANGEROUS.", aliases=["e", "ev"], name="eval")
@commands.check(is_owner)
async def _eval(ctx, *, code : str):
    """Evaluates some code. VERY DANGEROUS."""
    try:
        result = eval(code)
        if asyncio.iscoroutine(result):
            await result
        else:
            await ctx.send(wrap.format(result))
    except Exception as e: # pylint: disable=bare-except
        await ctx.send(wrap.format(type(e).__name__ + ': ' + str(e)))



@bot.command()
async def error():
    3/0

async def on_command_error(ctx, exc):
    e = f"{type(exc).__name__}: {exc}"
    emb = discord.Embed(
        title=":warning: An error occurred",
        color=discord.Colour.red(),
        description="Please report this error to the bot's developers, so it will be fixed as fast as possible. Provide details of what you did for this to happen, along with the full Traceback below.",
        url="http://github.com/Terminal/DiscordBot"
    )
    emb.add_field("Traceback", f"```\n{e}```")

if __name__ == "__main__": 
    for ext in startup_exts:
        try:
            print("Loading extension {}".format(ext))
            bot.load_extension("extensions."+ext)
        except Exception as e:  # pylint: disable=bare-except
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load {}:\n{}".format(ext, exc))
    bot.run(config["token"])
