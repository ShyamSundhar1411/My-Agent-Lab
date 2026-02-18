import json
import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, is_separator_regex=False, length_function=len
)


def split_data_from_file(file: str):
    logger.info(f"Loading file: {file}")

    chunks_with_metadata = []

    try:
        with open(file, "r", encoding="utf-8") as f:
            file_as_object = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file: {file} | Error: {e}")
        raise

    if not isinstance(file_as_object, dict):
        logger.error(f"Invalid JSON structure in {file} (expected dict)")
        raise ValueError("JSON root must be an object/dict")

    keys = list(file_as_object.keys())
    logger.info(f"Found {len(keys)} top-level keys")

    form_name = file[file.rindex("/") + 1 : file.rindex(".")]

    total_chunks = 0

    for key in keys:
        item_text = file_as_object.get(key)

        if not isinstance(item_text, str):
            logger.warning(f"Skipping key '{key}' (not a string)")
            continue

        item_text_chunks = text_splitter.split_text(item_text)
        logger.info(f"Key '{key}' split into {len(item_text_chunks)} chunks")

        for chunk_seq_id, chunk in enumerate(item_text_chunks):
            chunk_id = f"{form_name}#{key}#{chunk_seq_id}"

            chunks_with_metadata.append(
                {
                    "text": chunk,
                    "formItem": key,
                    "chunkSeqId": chunk_seq_id,
                    "chunkId": chunk_id,
                    "source": file_as_object.get("source"),
                }
            )

            logger.debug(f"📄 Created chunk: {chunk_id}")
            chunk_seq_id += 1
            total_chunks += 1

    logger.info(f"Chunking complete | Total chunks created: {total_chunks}")

    return chunks_with_metadata
