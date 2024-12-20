import cv2
import numpy as np

# Parâmetros do marcador ArUco
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
ARUCO_PARAMS = cv2.aruco.DetectorParameters()

# Dimensão real do lado do marcador ArUco em milímetros
ARUCO_SIDE_MM = 50  # Tamanho do marcador em mm

# Parâmetros da câmera (matriz da câmera e coeficientes de distorção)
camera_matrix = np.array([[629.6773429443547, 0.0, 320.1018395309984],
                          [0.0, 633.5957130027031, 242.57966399911092],
                          [0.0, 0.0, 1.0]])

dist_coeff = np.array([0.029001373916050614, -0.3362041074876886, 0.0056021105323758045,
                       -0.005311479113024399, 0.7661077524826636])
# Inicializar a captura da webcam
cap = cv2.VideoCapture(4)  # Substituir '4' pelo índice correto da câmera, se necessário

# Checar se a webcam abriu corretamente
if not cap.isOpened():
    print("Erro ao abrir a webcam.")
    exit()

# Função para calcular a distância euclidiana entre dois pontos
def euclidean_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

# Função para medir objetos e desenhar as caixas com dimensões
def measure_object(image, scale):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    measurements = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 5 and h > 5:  # Ignorar ruídos pequenos
            # Calcular as dimensões do objeto em milímetros
            dimA = euclidean_distance((x, y), (x + w, y)) / scale  # Tamanho horizontal em mm
            dimB = euclidean_distance((x, y), (x, y + h)) / scale  # Tamanho vertical em mm

            measurements.append((dimA, dimB))  # Armazenar as dimensões

            # Desenhar o contorno e as dimensões
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            box_text = f"{dimA:.1f}mm x {dimB:.1f}mm"
            text_size, _ = cv2.getTextSize(box_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_w, text_h = text_size

            # Desenhar o fundo do texto
            cv2.rectangle(image, (x, y - text_h - 5), (x + text_w, y), (0, 255, 0), -1)
            # Colocar o texto na imagem
            cv2.putText(image, box_text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return measurements

print("Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame.")
        break

    # Corrigir distorção da imagem usando a matriz de calibração
    frame_undistorted = cv2.undistort(frame, camera_matrix, dist_coeff)

    # Detectar marcadores ArUco no frame corrigido
    gray = cv2.cvtColor(frame_undistorted, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMS)

    # Se marcadores forem detectados
    if ids is not None:
        for corner, marker_id in zip(corners, ids.flatten()):
            # Obter os 4 cantos do marcador
            points = corner[0]

            # Desenhar o contorno do marcador
            cv2.polylines(frame_undistorted, [np.int32(points)], True, (0, 255, 0), 2)

            # Calcular a escala em pixels por milímetro
            pixel_width = euclidean_distance(points[0], points[1])  # Distância entre dois pontos adjacentes
            pixels_per_mm = pixel_width / ARUCO_SIDE_MM

            # Identificar o centro do marcador
            center_x = int(np.mean(points[:, 0]))
            center_y = int(np.mean(points[:, 1]))

            # Mostrar a identificação do marcador
            cv2.putText(frame_undistorted, f"ID: {marker_id}", (center_x - 20, center_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Medir os objetos na imagem usando a escala
            measurements = measure_object(frame_undistorted, pixels_per_mm)

            # Exibir as medições para depuração
            for i, (dimA, dimB) in enumerate(measurements):
                print(f"Objeto {i + 1}: {dimA:.2f}mm x {dimB:.2f}mm")

    # Mostrar o frame corrigido na tela
    cv2.imshow("ArUco Detection and Measurement", frame_undistorted)

    # Sair do loop ao pressionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
