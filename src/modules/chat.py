from modules import config
from discord import Message, File
from discord.ext import commands
import typing, time, random, numpy as np
import google.generativeai as genai
sdbc = config.spdb["qna"]["query"]
bws = set(config.bws)
datasets:dict = sdbc.find()
generation_config = {"temperature": 1.5,"top_p": 0.95,"top_k": 64,"max_output_tokens": 2000}
try:genai.configure(api_key=config.GEMAPI)
except Exception as e:config.webpost(url=config.dml, json={"content":f"```py\n{e}\n```"})
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
say = ["bolo ki", "say", "bolo", "bolie", "kaho"]
name = {"my name", "mera nam kya hai", "what is my name", "do you know my name"}
unfair = [{"q":"me harami", "a":"aap harami ho"}, {"q":"me useless", "a":"me really useful yes i know"}, {"q":"mein harami", "a":"aap harami nehi ho!! kya baat kar rhe ho"}, {"q":"i am a dog", "a":"im a bot!! Spruce Bot 😎"}]
repl_yes = ["ohh", "okey", "hm"]
history=[
    {"role": "user","parts": ["what is your name?"]},
    {"role": "model","parts": ["im spruce!! an awesome discord bot. nice to meet you btw!!"]},
    {"role": "user","parts": ["what you can do?"]},
    {"role": "model","parts": ["i can manage tournaments, chat with you, play music, moderate your server, and many more things!!"]}
    ]



class ChatClient:
    """
    A class to chat with user
    """
    def __init__(self, bot) -> None:
        self.bot:commands.Bot = bot
        self.chat_session = model.start_chat(history=history)

    async def lang_model(self, ctx:commands.Context, query:str) -> typing.Union[str, None]:
        if "yes" in query:return random.choice(repl_yes)
        for i in name:
            if i in query:return ctx.author.name
        said = set(query.lower().split()).intersection(say)
        if said:
                for i in said:query = query.replace(i, "")
                for j in unfair:
                    if j["q"] in query:query = query.replace(j["q"], j["a"])
                return query
        return None

    def is_bws(self, query:str) -> bool:
        bw = set(query.lower().split())
        if len(bws.intersection(bw)) > 0:return True

    def check_send(self, ctx:commands.Context, message:Message, bot:commands.Bot) -> bool|None:
        """return `True` if triggered dm or mentioned in channel, else `None`"""
        if ctx.author.bot:return None
        elif not message.guild:return True
        elif not message.reference or not message.reference.resolved:return False
        elif message.reference.resolved.author.id == bot.user.id:return True
        return None
        
    def query(self, response:list[dict[str,str]], query:str) -> typing.Union[str, None]:
        if self.is_bws(query):return "Message contains blocked word. so i can't reply to this message! sorry buddy."
        matches = []
        for a in response:
            a2 = np.array([x.lower() for x in a["q"].split()])
            a1 = np.array([x.lower() for x in query.split()])
            same = len(np.intersect1d(a1, a2))
            if int(same/len(a1)*100) >= 95:return a["a"]
            if same >= len(query.split())/2:
                if int(same/len(a1)*100) > 40:matches.append({"a" : a["a"], "r": int(same/len(a1)*100)})
        if len(matches) > 0:return max(matches, key=lambda x: x['r'])["a"]
        if len(matches)==0:return None


    async def chat(self, message:Message):
        try:
            ctx = await self.bot.get_context(message)
            if not self.check_send(ctx, message, self.bot):return
            await ctx.typing()
            messages = [message async for message in ctx.channel.history(limit=16)][::-1]
            self.chat_session.history = history
            for message in messages:
                if not message.author.bot:self.chat_session.history.append({"role": "user","parts": [message.content]})
                elif message.author.bot: self.chat_session.history.append({"role": "model","parts": [message.content]})
            text = message.content.replace(F"<@{self.bot.user.id}>", "")
            if await self.lang_model(ctx, message.content):return await message.reply(await self.lang_model(ctx, text))
            response = self.query(datasets, text)
            if response:return await message.reply(response)
            else:
                response = self.chat_session.send_message(text).text
                if len(response) > 2000:
                    with open("response.txt", "w") as f:f.write(response)
                    return await message.reply(file=File("response.txt"))
                else:return await message.reply(response)
        except Exception as e:config.webpost(url=config.dml, json={"content":f"{message.author}```\n{e}\n```"})

