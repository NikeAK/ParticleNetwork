from core.root import Core


class App:
    def __init__(self) -> None:
        self.__core = Core()

    def start(self):
        self.__core.initialization()


if __name__ == '__main__':
    app = App()
    app.start()

