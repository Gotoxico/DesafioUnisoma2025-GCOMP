class BaseLoader:
    def __init__(self, filename, chunk_size):
        self.filename = filename
        self.chunk_size = chunk_size
        self.chunks = []

    def load(self):
        raise NotImplementedError

class TxtLoader(BaseLoader):
    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.read().split('\n')
                n = len(lines)

                if 0 < self.chunk_size < 1:
                    self.chunk_size = len(lines) * self.chunk_size

                self.chunk_size = int(self.chunk_size)

                for i in range(0, n, self.chunk_size):
                    self.chunks.append('\n'.join(lines[i:i+self.chunk_size]))

        except FileNotFoundError:
            print(f"Erro: O arquivo {self.filename} não foi encontrado.")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")

if __name__ == '__main__':
    dl = TxtLoader('arquivos_ong/Meditação Avançada/2019 08 14 Meditação Avancada T2.txt', 0.1)
    dl.load()
    print(dl.chunks[0])