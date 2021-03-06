#!/usr/bin/env python3
# pylint: disable=C0103

"""Commands that invoke random things. Coin flips, dice rolls, kemonomimi... wait."""

import json
import random
import re

from discord.ext import commands

REGEX_DND = "[0-9]+[dD][0-9]+"
REGEX_DND_SPLIT = "[dD]"
REGEX_OBJECT_DND = re.compile(REGEX_DND)

MAX_ROLLS = 20
MAX_ROLL_SIZE = 30
MAX_DIE_SIZE = 2000

URL_RANDOM_WORD_API = "http://setgetgo.com/randomword/get.php"
URL_RANDOM_DOG_API = "https://random.dog/woof.json"
URL_RANDOM_CAT_API = "https://random.cat/meow"
URL_RANDOM_BIRB = "https://random.birb.pw/img/{0}"
URL_RANDOM_BIRB_API = "https://random.birb.pw/tweet.json/"
URL_RANDOM_NEKO_API = "https://nekos.life/api/neko"

systemrandom = random.SystemRandom()


def generate_roll(die_count, die_size):
    roll_ = []
    for times in range(0, die_count):
        roll_.append(systemrandom.randint(1, die_size))
    return roll_


def parse_roll(expression):
    expression_parts = re.split(REGEX_DND_SPLIT, expression)
    roll_ = tuple(int(value) for value in expression_parts)
    return roll_


def trim_expressions(*expressions):
    expressions = [e for e in expressions if REGEX_OBJECT_DND.fullmatch(e)]
    return expressions


def parse_rolls(*expressions, **kwargs):

    max_rolls = kwargs["max_rolls"]
    max_roll_size = kwargs["max_roll_size"]
    max_die_size = kwargs["max_die_size"]

    rolls = []

    expressions = trim_expressions(*expressions)

    for expression in expressions[:max_rolls]:

        roll_ = parse_roll(expression)

        if roll_[0] > max_roll_size or roll_[1] > max_die_size:
            continue

        elif roll_[1] > 1 and roll_[0] >= 1:
            outcome = generate_roll(roll_[0], roll_[1])
            rolls.append(f"{expression}: {outcome} ({sum(outcome)})")

    return rolls


class Random:
    """Commands that produce random outputs."""

    @commands.command(aliases=["doge"])
    @commands.cooldown(6, 12)
    async def dog(self, ctx):
        """Fetch a random dog."""
        async with ctx.bot.session.get(URL_RANDOM_DOG_API) as response:
            if response.status == 200:
                data = await response.text()
                doggo = json.loads(data)
                url = doggo["url"]
                await ctx.send(url)
            else:
                await ctx.send("Could not reach random.dog. :<")

    @commands.command(aliases=["feline"])
    @commands.cooldown(6, 12)
    async def cat(self, ctx):
        """Fetch a random cat."""
        async with ctx.bot.session.get(URL_RANDOM_CAT_API) as response:
            if response.status == 200:
                data = await response.text()
                catto = json.loads(data)
                url = catto["file"]
                await ctx.send(url)
            else:
                await ctx.send("Could not reach random.cat. :<")

    @commands.command(aliases=["kemonomimi", "catgirl", "kneko", "nekomimi",
                               "foxgirl" "kitsune", "kitsunemimi"])
    @commands.cooldown(6, 12)
    async def kemono(self, ctx):
        """Fetch a random animal-eared person."""
        async with ctx.bot.session.get(URL_RANDOM_NEKO_API) as response:
            if response.status == 200:
                neko = await response.json()
                url = neko["neko"]
                await ctx.send(url)
            else:
                await ctx.send("Could not reach nekos.life. :<")

    @commands.command()
    @commands.cooldown(6, 12)
    async def birb(self, ctx):
        """Fetch a random birb."""
        async with ctx.bot.session.get(URL_RANDOM_BIRB_API) as response:
            if response.status == 200:
                data = await response.text()
                borb = json.loads(data)
                url = URL_RANDOM_BIRB.format(borb["file"])
                await ctx.send(url)
            else:
                await ctx.send("Could not reach random.birb.pw. :<")

    @commands.command(aliases=["cflip", "coinflip"])
    @commands.cooldown(6, 12)
    async def coin(self, ctx):
        """Flip a coin."""
        choice = systemrandom.choice(["Heads!", "Tails!"])
        await ctx.send(choice)

    @commands.command(aliases=["rword", "randword"])
    @commands.cooldown(6, 12)
    async def rwg(self, ctx):
        """Randomly generate a word."""
        async with ctx.bot.session.get(URL_RANDOM_WORD_API) as response:
            if response.status == 200:
                word = await response.text()
                await ctx.send(word)
            else:
                await ctx.send("Could not reach API. x.x")

    @commands.command()
    @commands.cooldown(6, 12)
    async def roll(self, ctx, *expressions):
        """Roll some dice, using D&D syntax.

        Examples:
        roll 5d6 - Roll five six sided dice.
        roll 1d20 2d8 - Roll one twenty sided die, and two eight sided dice.
        """

        rolls = parse_rolls(*expressions,
                            max_rolls=MAX_ROLLS,
                            max_roll_size=MAX_ROLL_SIZE,
                            max_die_size=MAX_DIE_SIZE)

        if rolls:
            roll_join = "\n".join(rolls)
            await ctx.send(f"```{roll_join}```")

        else:
            await ctx.send(("No valid rolls supplied. "
                            f"Please use D&D format, e.g. 5d6.\n"
                            "Individual rolls cannot have more than "
                            f"{MAX_ROLL_SIZE} dice, and dice cannot have "
                            f"more than {MAX_DIE_SIZE} sides."))


def setup(bot):
    """Set up the extension."""
    bot.add_cog(Random())
