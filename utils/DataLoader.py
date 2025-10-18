from pypdf import PdfReader
from docx import Document
import math

MIN_CHUNK_SIZE = 10

class BaseLoader:
    def __init__(self, filename, chunk_size):
        self.filename = filename
        self.chunk_size = chunk_size
        self.chunks = []

    def load(self):
        raise NotImplementedError

    def _create_chunks(self, lines):
        n = len(lines)
        if n == 0:
            return

        # Calcula chunk_size correto
        if 0 < self.chunk_size < 1:
            chunk_size = max(1, math.ceil(n * self.chunk_size))
        else:
            chunk_size = math.ceil(self.chunk_size)
        chunk_size = max(MIN_CHUNK_SIZE, chunk_size)

        # Gera chunks
        for i in range(0, n, chunk_size):
            chunk = '\n'.join(lines[i:i + chunk_size])
            if chunk.strip():  # evita chunk vazio
                self.chunks.append(chunk)

    def __len__(self):
        return len(self.chunks)

class TxtLoader(BaseLoader):
    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = [line for line in file.read().split('\n') if line.strip() != '']
            self._create_chunks(lines)
        except FileNotFoundError:
            print(f"Erro: O arquivo {self.filename} não foi encontrado.")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")


class PdfLoader(BaseLoader):
    def load(self):
        try:
            reader = PdfReader(self.filename)
            lines = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    lines.extend([line for line in text.split('\n') if line.strip() != ''])
            self._create_chunks(lines)
        except FileNotFoundError:
            print(f"Erro: O arquivo {self.filename} não foi encontrado.")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")


class DocxLoader(BaseLoader):
    def load(self):
        try:
            reader = Document(self.filename)
            lines = [p.text for p in reader.paragraphs if p.text.strip() != '']
            self._create_chunks(lines)
        except FileNotFoundError:
            print(f"Erro: O arquivo {self.filename} não foi encontrado.")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")


if __name__ == '__main__':
    dl1 = PdfLoader('arquivos_ong/pdfs/O que é Filosofia afinal_. Qual sua utilidade, se é que há alguma_ _ by Leopoldo Luiz Diniz Lopes _ Disruptuose _ Medium.pdf', 0.01)
    dl1.load()
    print(dl1.chunks[0])
    print()

    dl2 = TxtLoader('arquivos_ong/Meditação Avançada/2019 07 24 Meditação Avançada T2.txt', 0.01)
    dl2.load()
    print(dl2.chunks[0])
    print()

    dl3 = DocxLoader('arquivos_ong/docx/O que é Filosofia afinal_. Qual sua utilidade, se é que há alguma_ _ by Leopoldo Luiz Diniz Lopes _ Disruptuose _ Medium.docx', 0.01)
    dl3.load()
    print()

    print(len(dl1))
    print(len(dl2))
    print(len(dl3))