import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, is_separator_regex=False, length_function=len
)


def split_data(data: dict, source_name: str = "document"):

    chunks_with_metadata = []

    if not isinstance(data, dict):
        logger.error("Invalid JSON structure in (expected dict)")
        raise ValueError("JSON root must be an object/dict")

    keys = list(data.keys())
    logger.info(f"Found {len(keys)} top-level keys")

    total_chunks = 0

    for key in keys:
        item_text = data.get(key)

        if not isinstance(item_text, str):
            logger.warning(f"Skipping key '{key}' (not a string)")
            continue

        item_text_chunks = text_splitter.split_text(item_text)
        logger.info(f"Key '{key}' split into {len(item_text_chunks)} chunks")

        for chunk_seq_id, chunk in enumerate(item_text_chunks):
            chunk_id = f"{source_name}#{key}#{chunk_seq_id}"

            chunks_with_metadata.append(
                {
                    "text": chunk,
                    "formItem": key,
                    "chunkSeqId": chunk_seq_id,
                    "chunkId": chunk_id,
                    "source": source_name,
                }
            )

            logger.debug(f"📄 Created chunk: {chunk_id}")
            chunk_seq_id += 1
            total_chunks += 1

    logger.info(f"Chunking complete | Total chunks created: {total_chunks}")

    return chunks_with_metadata
