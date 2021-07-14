# Uvindu Bro <https://t.me/UvinduBro>
# @Uvindu_Bro

from telethon import TelegramClient, events, Button
from urldownload import download_file
from config import BOTTOKEN, APIID, APIHASH, DOWNLOADPATH, USERNAME
import os
import time
import datetime
import asyncio
import aiohttp
from handlers import progress, humanbytes, time_formatter, convert_from_bytes
import traceback

bot = TelegramClient('UvinduBro', APIID, APIHASH).start(bot_token=BOTTOKEN)

def get_date_in_two_weeks():
   
    #get maximum date of storage for file by returns date in two weeks
    today = datetime.datetime.today()
    date_in_two_weeks = today + datetime.timedelta(days=14)
    return date_in_two_weeks.date()

async def send_to_transfersh_async(file):
    
    size = os.path.getsize(file)
    size_of_file = humanbytes(size)
    final_date = get_date_in_two_weeks()
    file_name = os.path.basename(file)

    print("\n📁 Uploading file: {} (size of the file: {})".format(file_name, size_of_file))
    url = 'https://transfer.sh/'
    
    with open(file, 'rb') as f:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={str(file): f}) as response:
                    download_link =  await response.text()
                    
    print("Link to download file (will be saved till {}):\n{}".format(final_date, download_link))
    return download_link, final_date, size_of_file


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    #send a message when the command /start is issued.
    await event.respond('Hello, I am Upload Bot.\n\nSend me any direct link and reply it with /upload for upload it to Telegram as file.\n\nSend me any file and reply it with /transfersh to generate direct download link of that file.\n\nA bot by @Uvindu_Bro 🇱🇰',
                         buttons=[
                        [Button.url("📦 Source Code", url="https://github.com/eleUploadBot"),
                         Button.url("🔊 Channel", url="https://t.me/UvinduBro")]])
                     
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/upload'))
async def up(event):
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("📥 Downloading 📥")
        
        try:
            filename = os.path.join(DOWNLOADPATH, os.path.basename(url.text))
            file_path = await download_file(url.text, filename, ilk, start, bot)
        except Exception as e:
            print(e)
            await event.respond(f"Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()

        try:
            orta = await event.respond("📤 Uploading to Telegram 📤")

            dosya = await bot.upload_file(filename, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, orta, start, "Uploading to Telegram...")
                ))

            zaman = str(time.time() - start)
            await bot.send_file(event.chat.id, dosya, force_document=True, caption=f"Uploaded By {USERNAME}")
        except Exception as e:
            traceback.print_exc()

            print(e)
            await event.respond(f"Uploading Failed\n\n**Error:** {e}")
        
        await orta.delete()

    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/transfersh'))
async def tsh(event):
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("📥 Downloading 📥")
        try:
            file_path = await url.download_media(progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, ilk, start, "📥 Downloading 📥")
                ))
        except Exception as e:
            traceback.print_exc()
            print(e)
            await event.respond(f"❌ Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()

        try:
            orta = await event.respond("📤 Uploading to TransferSh 📤")
            download_link, final_date, size = await send_to_transfersh_async(file_path)

            zaman = str(time.time() - start)
            await orta.edit(f"File Successfully Uploaded to TransferSh.\n\n🔗 Link  {download_link}\n📅 Expired Date {final_date}\n\n~By @UvinduBro 🇱🇰 ~")
        except Exception as e:
            traceback.print_exc()
            print(e)
            await event.respond(f"❌ Uploading Failed\n\n**Error:** {e}")

    raise events.StopPropagation


def main():
    if not os.path.isdir(DOWNLOADPATH):
        os.mkdir(DOWNLOADPATH)

    #start the bot.
    print("\n✅ Your bot started!\n\nDo visit @UvinduBro")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
