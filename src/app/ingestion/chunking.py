import re
from typing import List, Tuple
from app.core.types import Chunk, DocumentMeta
from app.core.utils import sha1_text
from app.core.logging import logger

TABLE_ROW_RE = re.compile(r"^\|.*\|$")

def _is_table_block(lines: List[str], i: int) -> bool:
    # Heurística: linha pipe + próxima linha separador de tabela
    if i + 1 >= len(lines):
        return False
    if not TABLE_ROW_RE.match(lines[i].strip()):
        return False
    return bool(re.match(r"^\|\s*:?[-]+:?\s*(\|\s*:?[-]+:?\s*)+\|?$", lines[i + 1].strip()))

def _read_table(lines: List[str], start: int) -> Tuple[str, int]:
    buf = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        buf.append(lines[i])
        i += 1
    return "\n".join(buf).strip(), i

def _is_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,6}\s+\S+", line.strip()))

def _heading_level(line: str) -> int:
    return len(line.split(" ")[0])  # número de #

class AdaptiveMarkdownChunker:
    """
    Chunking por estrutura: headings -> seções, tabelas como blocos atômicos.
    """

    def chunk(self, md_text: str, meta: DocumentMeta, max_chars: int = 2500) -> List[Chunk]:
        lines = md_text.splitlines()
        section_stack: List[str] = []
        blocks: List[Tuple[str, str]] = []  # (kind, text)

        i = 0
        while i < len(lines):
            line = lines[i]

            if _is_heading(line):
                level = _heading_level(line)
                title = line.strip().lstrip("#").strip()

                # ajusta stack de seção
                while len(section_stack) >= level:
                    section_stack.pop()
                section_stack.append(title)
                i += 1
                continue

            if _is_table_block(lines, i):
                table_text, next_i = _read_table(lines, i)
                blocks.append(("table", table_text))
                i = next_i
                continue

            # texto normal: acumula até próximo heading ou tabela
            buf = [line]
            i += 1
            while i < len(lines) and (not _is_heading(lines[i])) and (not _is_table_block(lines, i)):
                buf.append(lines[i])
                i += 1
            text_block = "\n".join(buf).strip()
            if text_block:
                blocks.append(("text", text_block))

        # agora “empacota” blocos respeitando max_chars sem quebrar tabela
        chunks: List[Chunk] = []
        current: List[str] = []
        current_kind = "text"
        order = 0

        def flush():
            nonlocal order
            if not current:
                return
            joined = "\n\n".join(current).strip()
            chunk_id = sha1_text(f"{meta.doc_id}|{order}|{joined[:200]}")
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    doc_id=meta.doc_id,
                    text=joined,
                    chunk_kind=current_kind,  # se misturar, fica "text"
                    section_path=list(section_stack),
                    order=order,
                    metadata={
                        "company": meta.company or "",
                        "doc_type": meta.doc_type or "",
                        "doc_date": meta.doc_date or "",
                    },
                )
            )
            order += 1
            current.clear()

        for kind, btext in blocks:
            if kind == "table":
                # nunca mistura tabela com outros conteúdos: flush antes e depois
                flush()
                current_kind = "table"
                current.append(btext)
                flush()
                current_kind = "text"
                continue

            # texto: agrega até max_chars
            if sum(len(x) for x in current) + len(btext) > max_chars and current:
                flush()
            current_kind = "text"
            current.append(btext)

        flush()
        logger.info("chunking.done", doc_id=meta.doc_id, n_chunks=len(chunks))
        return chunks
