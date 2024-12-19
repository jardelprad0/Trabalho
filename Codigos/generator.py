import cv2
import cv2.aruco as aruco

# Define o dicionário de marcadores ArUco (exemplo: DICT_4X4_50)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# Define o ID do marcador e o tamanho da imagem
marker_id = 0  # ID do marcador (entre 0 e o número máximo permitido pelo dicionário)
marker_size = 200  # Tamanho do marcador em pixels

# Verifica se o ID do marcador é válido
if marker_id >= aruco_dict.bytesList.shape[0]:
    raise ValueError(f"ID inválido! O ID deve estar entre 0 e {aruco_dict.bytesList.shape[0] - 1}.")

# Gera o marcador
marker_image = aruco.generateImageMarker(aruco_dict, marker_id, marker_size)

# Salva o marcador como uma imagem
output_path = "aruco_marker_id_0.png"
cv2.imwrite(output_path, marker_image)

print(f"Marcador ArUco com ID {marker_id} gerado e salvo como {output_path}")
