################################################################################################
# Author: Aniket Mirajkar
# Python script for auto check-in on hoyolab
# This script is inspired from the github user torikushiii's helper project and all credit goes to the original developer
################################################################################################

import requests
import discord
import config
import asyncio
from aiohttp import ClientSession
 
cookie = config.cookie
actID = config.actID
gameIcon = config.gameIcon
userAgent = config.userAgent
discordWebhook = config.discordWebhook
avatarLink = config.avatarLink
api = config.api
gameName = config.gameName
playerTitle = config.playerTitle
discordUserName = config.discordUserName


class Discord:
    async def send(self, data: dict, logged = False):
        
        if logged == True:    
            embed = discord.Embed(
                        description = data['message'],
                        color = 0xBB0BB5,
            )
            
            embed.set_author(name = gameName, icon_url = gameIcon)
            
            async with ClientSession() as session:
                webhook = discord.Webhook.from_url(discordWebhook, session = session)

                await webhook.send(embed = embed, username = discordUserName, avatar_url = avatarLink)
        else:    
            embed = discord.Embed(
                description = f"Today's reward: {data['award']['name']} x{data['award']['count']}\nTotal signed: {data['signed']}",
                color = 0xBB0BB5,
            )

            embed.set_author(name = gameName, icon_url = gameIcon)

            async with ClientSession() as session:
                webhook = discord.Webhook.from_url(discordWebhook, session = session)

                await webhook.send(embed = embed, username = discordUserName, avatar_url = avatarLink)

class Hoyo:

    @staticmethod
    async def sign():
        
        payload = {'act_id': actID}

        headers = {'User-Agent': userAgent,'Cookie': cookie}

        response = requests.post(f"{api}/sign", json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Sign HTTP Error: {response.status_code}")
            
        body = response.json()

        if body['retcode'] != 0 and body['message'] != 'OK':
            raise Exception(f"Sign API Error: {body['message']}")
            
        return True

    @staticmethod
    async def getInfo():

        headers = {'User-Agent': userAgent,'Cookie': cookie}

        response = requests.get(f"{api}/info?act_id={actID}", headers=headers)

        if response.status_code != 200:
            raise Exception(f"Info HTTP error: {response.status_code}")

        body = response.json()
            
        if body['retcode'] != 0 and body['message'] != "OK":
            raise Exception(f"Info API error: {body['message']}")

        return body['data']

    @staticmethod
    async def getAwards():
        
        headers = {'User-Agent': userAgent,'Cookie': cookie}

        response = requests.get(f"{api}/home?act_id={actID}", headers=headers)

        if response.status_code != 200:
            raise Exception(f"HTTP error: {response.status_code}")

        body = response.json()

        if body['retcode'] != 0 and body['message'] != "OK":
            raise Exception(f"API error: {body['message']}")

        return body['data']['awards']


    async def run():
        
        info = await Hoyo.getInfo()
        
        awards = await Hoyo.getAwards()

        if len(awards) == 0:
            print(f"There's no awards to claim(?)")

        data = {
                "today": info['today'],
                "total": info['total_sign_day'],
                "issigned": info['is_sign'],
                "missed": info['sign_cnt_missed']
        }

        discord = Discord()

        if data['issigned']:
            msg = {"message": f"You've already checked in today, {playerTitle}~"}
            await discord.send(msg, True)
            print(f"You've already checked in today, {playerTitle}~")

        total_signed = data['total']
        award_data = {
            "name": awards[total_signed]['name'],
            "count": awards[total_signed]['cnt']
        }

        Sign = await Hoyo.sign()
                
        if Sign:
            print(f"Signed in successfully! You have signed in for {data['total']} days!")
            print(f"You have received {award_data['count']} x {award_data['name']}!")

            if not discordWebhook or not isinstance(discordWebhook, str):
                print("No webhook provided")
                return True
            awrd = {"signed": data['total'], "award": award_data}
            await discord.send(awrd)


asyncio.run(Hoyo.run())



