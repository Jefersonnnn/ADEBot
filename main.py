from adebot.app import main


def run_app():
    app = main()
    app.run_polling()


if __name__ == "__main__":
    run_app()
