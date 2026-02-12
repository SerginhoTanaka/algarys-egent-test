import re
from typing import List, Tuple
from langchain_text_splitters import MarkdownHeaderTextSplitter

from app.core.types import Chunk, DocumentMeta
from app.core.utils import sha1_text
from app.core.logging import logger


# ---------------------------
#   DETECÇÃO DE TABELAS
# ---------------------------

# Linha de tabela: | ... |
TABLE_LINE_RE = re.compile(r"^\|.*\|$")

# Linha separadora de tabela: |---|---|
SEPARATOR_RE = re.compile(
    r"^\|\s*:?[-]+:?\s*(\|\s*:?[-]+:?\s*)+\|$"
)


def is_table_start(lines: List[str], i: int) -> bool:
    """
    Detecta início de tabela olhando duas linhas:
    - Primeira linha: conteúdo de tabela
    - Segunda linha: separador
    """
    if i + 1 >= len(lines):
        return False
    return bool(TABLE_LINE_RE.match(lines[i])) and bool(SEPARATOR_RE.match(lines[i + 1]))


def read_full_table(lines: List[str], start: int) -> Tuple[str, int]:
    """
    Lê a tabela inteira e retorna:
    (texto_da_tabela, índice_da_próxima_linha_depois_da_tabela)
    """
    buf = []
    i = start
    while i < len(lines) and TABLE_LINE_RE.match(lines[i]):
        buf.append(lines[i])
        i += 1

    return "\n".join(buf), i


# ---------------------------
#  CHUNKER BASEADO EM LC
# ---------------------------

class AdaptiveMarkdownChunker:
    """
    Agora com garantia absoluta de:
        - NENHUMA tabela é quebrada
        - Tabelas são blocos atômicos isolados
        - Chunk pequeno é juntado apenas com texto (NUNCA com tabela)
    """

    def __init__(self, max_chars: int = 2500, min_chars: int = 400):
        self.max_chars = max_chars
        self.min_chars = min_chars

        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
                ("####", "h4"),
                ("#####", "h5"),
                ("######", "h6"),
            ],
            strip_headers=False,
        )

    def extract_blocks(self, text: str) -> List[Tuple[str, str]]:
        """
        Divide o texto em blocos atômicos:
           ("table", tabela_inteira)
           ("text", parágrafo_ou_conjunto)
        """

        lines = text.splitlines()
        blocks = []

        i = 0
        while i < len(lines):

            # 🔥 DETECTA BLOCO DE TABELA (Átomo Absoluto)
            if is_table_start(lines, i):
                tbl, next_i = read_full_table(lines, i)
                blocks.append(("table", tbl))
                i = next_i
                continue

            # Caso contrário, texto normal
            buf = [lines[i]]
            i += 1
            while i < len(lines) and not is_table_start(lines, i):
                buf.append(lines[i])
                i += 1

            txt = "\n".join(buf).strip()
            if txt:
                blocks.append(("text", txt))

        return blocks

    def merge_small_text_chunks(self, blocks: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Junta apenas chunks TEXT pequenos.
        NUNCA junta tabela com texto.
        NUNCA divide tabela.
        """

        merged = []
        text_buffer = ""

        for kind, block in blocks:
            if kind == "table":
                # Se tinha texto acumulado, salva antes
                if text_buffer.strip():
                    merged.append(("text", text_buffer.strip()))
                    text_buffer = ""
                # tabela é atômica
                merged.append(("table", block))
                continue

            # É texto
            if len(block) < self.min_chars:
                text_buffer += "\n\n" + block
                if len(text_buffer) >= self.min_chars:
                    merged.append(("text", text_buffer.strip()))
                    text_buffer = ""
            else:
                # buffer pendente?
                if text_buffer.strip():
                    merged.append(("text", text_buffer.strip()))
                    text_buffer = ""
                merged.append(("text", block))

        if text_buffer.strip():
            merged.append(("text", text_buffer.strip()))

        return merged

    def _section_path(self, metadata: dict) -> List[str]:
        keys = ["h1", "h2", "h3", "h4", "h5", "h6"]
        return [metadata[k] for k in keys if k in metadata]

    # ---------------------------
    #       MÉTODO PRINCIPAL
    # ---------------------------

    def chunk(self, md_text: str, meta: DocumentMeta) -> List[Chunk]:
        sections = self.splitter.split_text(md_text)

        final_chunks: List[Chunk] = []
        order = 0

        for section in sections:
            section_path = self._section_path(section.metadata)

            # 1. Extrai tabelas separadamente
            blocks = self.extract_blocks(section.page_content)

            # 2. Junta apenas blocos TEXT pequenos
            blocks = self.merge_small_text_chunks(blocks)

            # 3. Monta chunks respeitando max_chars SEM quebrar tabela
            buffer_text = ""
            for kind, block in blocks:

                if kind == "table":
                    # Flush texto antes
                    if buffer_text.strip():
                        final_chunks.append(self._make_chunk(buffer_text, "text", section_path, meta, order))
                        order += 1
                        buffer_text = ""

                    # Adiciona tabela como chunk isolado
                    final_chunks.append(self._make_chunk(block, "table", section_path, meta, order))
                    order += 1
                    continue

                # Texto normal
                if len(buffer_text) + len(block) > self.max_chars and buffer_text.strip():
                    final_chunks.append(self._make_chunk(buffer_text, "text", section_path, meta, order))
                    order += 1
                    buffer_text = block
                else:
                    buffer_text += "\n\n" + block

            # resto pendente
            if buffer_text.strip():
                final_chunks.append(self._make_chunk(buffer_text, "text", section_path, meta, order))
                order += 1

        logger.info("chunking.done", doc_id=meta.doc_id, n_chunks=len(final_chunks))
        return final_chunks

    # ---------------------------
    #   CRIAÇÃO DO CHUNK FINAL
    # ---------------------------

    def _make_chunk(self, text: str, kind: str, section_path: List[str], meta: DocumentMeta, order: int) -> Chunk:
        chunk_id = sha1_text(f"{meta.doc_id}|{order}|{text[:120]}")
        return Chunk(
            chunk_id=chunk_id,
            doc_id=meta.doc_id,
            text=text.strip(),
            chunk_kind=kind,
            section_path=section_path,
            order=order,
            metadata={
                "company": meta.company or "",
                "doc_type": meta.doc_type or "",
                "doc_date": meta.doc_date or "",
            },
        )
