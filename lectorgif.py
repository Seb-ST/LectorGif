import os
from datetime import datetime

def read_bytes(file, num_bytes):
    return file.read(num_bytes)

def get_gif_version(header):
    return header[3:].decode('ascii')

def get_logical_screen_descriptor(file):
    lsd = read_bytes(file, 7)
    width = int.from_bytes(lsd[0:2], byteorder='little')
    height = int.from_bytes(lsd[2:4], byteorder='little')
    packed_byte = lsd[4]
    global_color_flag = (packed_byte & 0b10000000) >> 7
    color_resolution = ((packed_byte & 0b01110000) >> 4) + 1
    global_color_table_size = 2 ** ((packed_byte & 0b00000111) + 1) if global_color_flag else None
    background_color_index = lsd[5]

    return {
        'width': width,
        'height': height,
        'color_resolution': color_resolution,
        'global_color_table_size': global_color_table_size,
        'background_color_index': background_color_index,
    }

def get_image_count_and_comments(file):
    image_count = 0
    comments = []
    while True:
        block_type = read_bytes(file, 1)
        if not block_type:
            break
        if block_type == b'\x2C':
            image_count += 1
            read_bytes(file, 9)
            lct_flag = read_bytes(file, 1)[0] & 0b10000000
            if lct_flag:
                local_color_table_size = 2 ** ((read_bytes(file, 1)[0] & 0b00000111) + 1)
                read_bytes(file, 3 * local_color_table_size)
            read_bytes(file, 1)
            while True:
                data_block_size = read_bytes(file, 1)[0]
                if data_block_size == 0:
                    break
                read_bytes(file, data_block_size)
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
        elif block_type == b'\x3B':
            break
        else:
            read_bytes(file, 1)
    return image_count, comments

def get_file_dates(file_path):
    creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    modification_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    return creation_date, modification_date

def parse_gif_metadata(file_path):
    metadata = {}
    with open(file_path, 'rb') as f:
        header = read_bytes(f, 6)
        if header[:3] != b'GIF':
            raise ValueError("El archivo no es un GIF válido.")
        metadata['Número de versión'] = get_gif_version(header)
        lsd = get_logical_screen_descriptor(f)
        metadata['Tamaño de imagen'] = (lsd['width'], lsd['height'])
        metadata['Cantidad de colores'] = lsd['global_color_table_size'] if lsd['global_color_table_size'] else "No tiene tabla de colores global"
        metadata['Resolución de color'] = lsd['color_resolution']
        metadata['Color de fondo'] = lsd['background_color_index']
        metadata['Cantidad de imágenes'], metadata['Comentarios'] = get_image_count_and_comments(f)
    metadata['Fecha de creación'], metadata['Fecha de modificación'] = get_file_dates(file_path)
    return metadata

def save_metadata_to_txt(file_path, metadata):
    with open(file_path, 'a') as file:
        for key, value in metadata.items():
            file.write(f"{key}: {value}\n")
        file.write("\n" + "-" * 40 + "\n")

def recolectar_gifs(direccion_carpeta):
    gifs = []
    
    def explorar_carpeta(carpeta):
        for elemento in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, elemento)
            if os.path.isfile(ruta_completa) and ruta_completa.endswith('.gif'):
                gifs.append(ruta_completa)
            elif os.path.isdir(ruta_completa):
                explorar_carpeta(ruta_completa)
    
    explorar_carpeta(direccion_carpeta)
    return gifs
