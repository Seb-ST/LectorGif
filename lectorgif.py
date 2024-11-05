import os
from datetime import datetime

def read_bytes(file, num_bytes):
    """Lee un número específico de bytes de un archivo."""
    return file.read(num_bytes)

def get_gif_version(header):
    """Obtiene la versión del GIF a partir del encabezado."""
    return header[3:].decode('ascii')

def get_logical_screen_descriptor(file):
    """Lee y devuelve el Logical Screen Descriptor del archivo."""
    lsd = read_bytes(file, 7)
    width = int.from_bytes(lsd[0:2], byteorder='little')
    height = int.from_bytes(lsd[2:4], byteorder='little')
    
    packed_byte = lsd[4]
    global_color_flag = (packed_byte & 0b10000000) >> 7
    color_resolution = ((packed_byte & 0b01110000) >> 4) + 1
    global_color_table_size = 2 ** ((packed_byte & 0b00000111) + 1)
    background_color_index = lsd[5]

    return {
        'width': width,
        'height': height,
        'global_color_flag': global_color_flag,
        'color_resolution': color_resolution,
        'global_color_table_size': global_color_table_size,
        'background_color_index': background_color_index,
    }

def get_image_count_and_comments(file):
    """Cuenta la cantidad de imágenes y extrae comentarios del archivo."""
    image_count = 0
    comments = []

    while True:
        block_type = read_bytes(file, 1)
        if not block_type:
            break

        # Image Descriptor (0x2C)
        if block_type == b'\x2C':
            image_count += 1
            # Saltar el bloque de descriptor de imagen y datos comprimidos
            read_bytes(file, 8)  # Descriptor de imagen (8 bytes)
            lct_flag = read_bytes(file, 1)[0] & 0b10000000  # Local Color Table Flag
            if lct_flag:
                local_color_table_size = 2 ** ((read_bytes(file, 1)[0] & 0b00000111) + 1)
                read_bytes(file, 3 * local_color_table_size)  # Saltar tabla de colores local
            read_bytes(file, 1)  # LZW Minimum Code Size
            while True:
                data_block_size = read_bytes(file, 1)[0]
                if data_block_size == 0:
                    break
                read_bytes(file, data_block_size)

        # Comment Extension (0x21 0xFE)
        elif block_type == b'\x21':
            extension_label = read_bytes(file, 1)
            if extension_label == b'\xFE':
                comment_data = []
                while True:
                    sub_block_size = read_bytes(file, 1)[0]
                    if sub_block_size == 0:
                        break
                    comment_data.append(read_bytes(file, sub_block_size).decode('ascii'))
                comments.append("".join(comment_data))

        # Trailer (0x3B) - Final del archivo
        elif block_type == b'\x3B':
            break

        # Saltar otros bloques y extensiones
        else:
            read_bytes(file, 1)

    return image_count, comments

def get_file_dates(file_path):
    """Obtiene las fechas de creación y modificación del archivo."""
    creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    modification_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    return creation_date, modification_date

def parse_gif_metadata(file_path):
    """Función principal para parsear los metadatos del archivo GIF."""
    metadata = {}

    with open(file_path, 'rb') as f:
        # Leer el encabezado (6 bytes)
        header = read_bytes(f, 6)
        if header[:3] != b'GIF':
            raise ValueError("El archivo no es un GIF válido.")
        metadata['Número de versión'] = get_gif_version(header)

        # Obtener el Logical Screen Descriptor
        lsd = get_logical_screen_descriptor(f)
        metadata['Tamaño de imagen'] = (lsd['width'], lsd['height'])
        metadata['Cantidad de colores'] = lsd['global_color_table_size'] if lsd['global_color_flag'] else "No tiene tabla de colores global"
        metadata['Resolución de color'] = lsd['color_resolution']
        metadata['Color de fondo'] = lsd['background_color_index']

        # Obtener la cantidad de imágenes y comentarios
        metadata['Cantidad de imágenes'], metadata['Comentarios'] = get_image_count_and_comments(f)

    # Agregar fechas de creación y modificación
    metadata['Fecha de creación'], metadata['Fecha de modificación'] = get_file_dates(file_path)

    return metadata


# Ejemplo de uso
file_path = 'archivo.gif'
metadatos = parse_gif_metadata(file_path)
for clave, valor in metadatos.items():
    print(f"{clave}: {valor}")
