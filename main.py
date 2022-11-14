from config import dp, bot, app
import commands

async def main():
    async with app:
        me = await bot.get_me()
        print(me)
        await dp.skip_updates()
        await dp.start_polling()

if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        print("Goodbye!")
        exit()
