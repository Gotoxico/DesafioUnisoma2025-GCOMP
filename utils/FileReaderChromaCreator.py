from uuid import uuid4, uuid5, NAMESPACE_URL
import os

from langchain_core.documents import Document

from utils.DataLoader import TxtLoader, PdfLoader, DocxLoader

import hashlib

import unicodedata


def makeChunkID(file : str, index : int) -> str:
    name = f"{os.path.abspath(file)}_{index}"
    return str(uuid5(NAMESPACE_URL, name))

def contentHash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def getCollectionFromVectorStore(vector_store):
    if hasattr(vector_store, "_collection"):
        return vector_store._collection
    
    if hasattr(vector_store, "client") and hasattr(vector_store, "collection_name"):
        client = getattr(vector_store, "client")
        try:
            return client.get_collection(vector_store.collection_name)
        except Exception:
            return None
    return None

#Função para passar folder e pegar arquivos dentro
def carregarArquivosFolder(folderPath, chunkSize, vector_store, skipIfUnchanged):
    collection = getCollectionFromVectorStore(vector_store)

    for file in os.listdir(folderPath):
        if not (file.endswith(".txt") or file.endswith(".pdf") or file.endswith(".docx")):
            continue

        file_path = os.path.abspath(os.path.join(folderPath, file))

        if file.endswith(".txt"):
            loader = TxtLoader(file_path, chunkSize)
        elif file.endswith(".pdf"):
            loader = PdfLoader(file_path, chunkSize)
        else:
            loader = DocxLoader(file_path, chunkSize)

        loader.load()
        n_chunks = len(loader.chunks)
        print(f"{file_path} → {n_chunks} chunks")

        docs_to_upsert = []
        ids_to_upsert = []

        for i, chunk in enumerate(loader.chunks):
            chunk_id = makeChunkID(file_path, i)
            ch_hash = contentHash(chunk)
            metadata = {"source": f"{file_path}_{i}", "content_hash": ch_hash}

            should_upsert = True
            if skipIfUnchanged and collection is not None:
                try:
                    existing = collection.get(ids=[chunk_id], include=['metadatas', 'documents', 'ids'])
                    if existing and len(existing.get("ids", [])) > 0:
                        existing_meta = existing.get("metadatas", [{}])[0] or {}
                        existing_hash = existing_meta.get("content_hash")
                        if existing_hash == ch_hash:
                            should_upsert = False
                except Exception:
                    should_upsert = True

            if should_upsert:
                doc = Document(page_content=chunk, metadata=metadata, id=i)
                docs_to_upsert.append(doc)
                ids_to_upsert.append(chunk_id)

        if docs_to_upsert:
            vector_store.add_documents(documents=docs_to_upsert, ids=ids_to_upsert)
            print(f"Upserted {len(docs_to_upsert)} chunks for file {file_path}")
        else:
            print(f"No changes detected for file {file_path}; nothing upserted.")
    return True



#Função para carregar de um arquivo com path
def carregarArquivo(file, chunkSize, vector_store, skipIfUnchanged):
    collection = getCollectionFromVectorStore(vector_store)

    if file.endswith(".txt"):
            loader = TxtLoader(file, chunkSize)
    elif file.endswith(".pdf"):
        loader = PdfLoader(file, chunkSize)
    else:
        loader = DocxLoader(file, chunkSize)

    loader.load()
    n_chunks = len(loader.chunks)
    print(f"{file} → {n_chunks} chunks")

    docs_to_upsert = []
    ids_to_upsert = []

    for i, chunk in enumerate(loader.chunks):
        chunk_id = makeChunkID(file, i)
        ch_hash = contentHash(chunk)

        metadata = {"source": f"{file}_{i}", "content_hash": ch_hash}

        should_upsert = True
        if skipIfUnchanged and collection is not None:
            try:
                existing = collection.get(ids=[chunk_id], include=['metadatas', 'documents', 'ids'])
                if existing and len(existing.get("ids", [])) > 0:
                    existing_meta = existing.get("metadatas", [{}])[0] or {}
                    existing_hash = existing_meta.get("content_hash")
                    if existing_hash == ch_hash:
                        should_upsert = False
            except Exception:
                should_upsert = True

        if should_upsert:
            doc = Document(page_content=chunk, metadata=metadata, id=i)
            docs_to_upsert.append(doc)
            ids_to_upsert.append(chunk_id)

    if docs_to_upsert:
        vector_store.add_documents(documents=docs_to_upsert, ids=ids_to_upsert)
        print(f"Upserted {len(docs_to_upsert)} chunks for file {file}")
    else:
        print(f"No changes detected for file {file}; nothing upserted.")
    return True
