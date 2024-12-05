import os
import zlib
import gzip
import lzma
from typing import BinaryIO, Optional, Tuple
from io import BytesIO
from .models import CompressionType, CompressionInfo

class BackupCompressor:
    """Gerenciador de compressão de backups"""

    CHUNK_SIZE = 64 * 1024  # 64KB chunks para processamento em memória

    @staticmethod
    def _get_compressor(compression_type: CompressionType, level: int):
        """Retorna o compressor adequado para o tipo especificado"""
        if compression_type == CompressionType.ZLIB:
            return zlib.compressobj(level)
        elif compression_type == CompressionType.GZIP:
            return gzip.GzipFile(fileobj=BytesIO(), mode="wb", compresslevel=level)
        elif compression_type == CompressionType.LZMA:
            return lzma.LZMACompressor(preset=level)
        else:
            raise ValueError(f"Tipo de compressão não suportado: {compression_type}")

    @staticmethod
    def _get_decompressor(compression_type: CompressionType):
        """Retorna o decompressor adequado para o tipo especificado"""
        if compression_type == CompressionType.ZLIB:
            return zlib.decompressobj()
        elif compression_type == CompressionType.GZIP:
            return gzip.GzipFile(fileobj=BytesIO(), mode="rb")
        elif compression_type == CompressionType.LZMA:
            return lzma.LZMADecompressor()
        else:
            raise ValueError(f"Tipo de compressão não suportado: {compression_type}")

    def compress_file(self, 
                      source_path: str, 
                      dest_path: str, 
                      compression_type: CompressionType = CompressionType.ZLIB,
                      level: int = 6) -> Optional[CompressionInfo]:
        """Comprime um arquivo usando o algoritmo especificado"""
        try:
            if not os.path.exists(source_path):
                return None

            # Garante que o diretório de destino existe
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Inicializa compressor
            compressor = self._get_compressor(compression_type, level)
            original_size = os.path.getsize(source_path)
            compressed_size = 0

            with open(source_path, "rb") as src, open(dest_path, "wb") as dst:
                # Escreve cabeçalho com informações da compressão
                header = f"{compression_type}:{level}\n".encode()
                dst.write(header)
                compressed_size += len(header)

                # Processa o arquivo em chunks
                while chunk := src.read(self.CHUNK_SIZE):
                    if isinstance(compressor, gzip.GzipFile):
                        compressor.write(chunk)
                        compressed = compressor.fileobj.getvalue()
                        compressor.fileobj.seek(0)
                        compressor.fileobj.truncate()
                    else:
                        compressed = compressor.compress(chunk)
                    if compressed:
                        dst.write(compressed)
                        compressed_size += len(compressed)

                # Finaliza compressão
                if isinstance(compressor, gzip.GzipFile):
                    compressor.close()
                    final = compressor.fileobj.getvalue()
                else:
                    final = compressor.flush()
                if final:
                    dst.write(final)
                    compressed_size += len(final)

            # Calcula taxa de compressão
            ratio = original_size / compressed_size if compressed_size > 0 else 1.0

            return CompressionInfo(
                type=compression_type,
                original_size=original_size,
                compressed_size=compressed_size,
                ratio=ratio,
                level=level
            )

        except Exception as e:
            print(f"Erro ao comprimir arquivo {source_path}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return None

    def decompress_file(self, 
                        source_path: str, 
                        dest_path: str) -> Tuple[bool, Optional[str]]:
        """Descomprime um arquivo"""
        try:
            if not os.path.exists(source_path):
                return False, "Arquivo comprimido não encontrado"

            # Garante que o diretório de destino existe
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            print(f"Descomprimindo {source_path} para {dest_path}")

            with open(source_path, "rb") as src:
                # Lê cabeçalho
                header = src.readline().decode().strip()
                print(f"Cabeçalho: {header}")
                compression_type, level = header.split(":")
                compression_type = CompressionType(compression_type)
                print(f"Tipo de compressão: {compression_type}, nível: {level}")

                # Inicializa decompressor
                decompressor = self._get_decompressor(compression_type)

                # Lê todo o conteúdo comprimido
                compressed_data = src.read()
                print(f"Tamanho dos dados comprimidos: {len(compressed_data)} bytes")

                with open(dest_path, "wb") as dst:
                    if isinstance(decompressor, gzip.GzipFile):
                        decompressor.fileobj = BytesIO(compressed_data)
                        decompressed = decompressor.read()
                        dst.write(decompressed)
                    else:
                        # Para ZLIB e LZMA, processa em chunks
                        decompressed = decompressor.decompress(compressed_data)
                        dst.write(decompressed)
                        final = decompressor.flush()
                        if final:
                            dst.write(final)

            print(f"Arquivo descomprimido com sucesso: {os.path.exists(dest_path)}")
            return True, None

        except Exception as e:
            print(f"Erro ao descomprimir arquivo {source_path}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return False, str(e)

    def compress_directory(self,
                          source_dir: str,
                          dest_dir: str,
                          compression_type: CompressionType = CompressionType.ZLIB,
                          level: int = 6) -> Optional[CompressionInfo]:
        """Comprime um diretório inteiro"""
        try:
            if not os.path.exists(source_dir):
                return None

            total_original_size = 0
            total_compressed_size = 0

            # Processa cada arquivo no diretório
            for root, _, files in os.walk(source_dir):
                for file in files:
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(source_path, source_dir)
                    dest_path = os.path.join(dest_dir, rel_path + ".compressed")

                    # Comprime arquivo individual
                    info = self.compress_file(
                        source_path, dest_path, compression_type, level)
                    
                    if info:
                        total_original_size += info.original_size
                        total_compressed_size += info.compressed_size

            if total_original_size > 0:
                ratio = total_original_size / total_compressed_size
                return CompressionInfo(
                    type=compression_type,
                    original_size=total_original_size,
                    compressed_size=total_compressed_size,
                    ratio=ratio,
                    level=level
                )

            return None

        except Exception as e:
            print(f"Erro ao comprimir diretório {source_dir}: {e}")
            return None

    def decompress_directory(self,
                            source_dir: str,
                            dest_dir: str) -> Tuple[bool, Optional[str]]:
        """Descomprime um diretório inteiro"""
        try:
            if not os.path.exists(source_dir):
                return False, "Diretório comprimido não encontrado"

            print(f"Descomprimindo diretório {source_dir} para {dest_dir}")
            success = True
            error_msg = None

            # Processa cada arquivo no diretório
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith(".compressed"):
                        source_path = os.path.join(root, file)
                        rel_path = os.path.relpath(source_path, source_dir)
                        # Remove .compressed do nome do arquivo
                        base_path = rel_path[:-10]  # Remove .compressed
                        dest_path = os.path.join(dest_dir, base_path)

                        print(f"Processando arquivo {source_path}")
                        # Descomprime arquivo individual
                        ok, err = self.decompress_file(source_path, dest_path)
                        if not ok:
                            success = False
                            error_msg = err
                            break

            print(f"Descompressão do diretório concluída: {success}")
            return success, error_msg

        except Exception as e:
            print(f"Erro ao descomprimir diretório {source_dir}: {e}")
            return False, str(e)

