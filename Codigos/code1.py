import cv2
import numpy as np

# Configurações do tabuleiro
GRID_SIZE_MM = 15  # Tamanho da célula em mm
GRID_ROWS, GRID_COLS = 10, 10

# Função para encontrar o tabuleiro
def find_chessboard(image, grid_size):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, grid_size, None)
    return found, corners

# Função para calcular a escala pixel/mm
def calculate_scale(corners):
    if corners is not None:
        # Calcula a distância média entre os primeiros pontos
        dist = np.linalg.norm(corners[0] - corners[1])  # Distância entre dois pontos adjacentes
        scale = GRID_SIZE_MM / dist
        return scale
    return None

# Função para medir objetos e desenhar as caixas com dimensões
def measure_object(image, scale):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    measurements = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 5 and h > 5:  # Ignorar ruídos pequenos
            width_mm = w * scale
            height_mm = h * scale
            measurements.append((width_mm, height_mm))

            # Desenhar o contorno e as dimensões
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            box_text = f"{width_mm:.1f}mm x {height_mm:.1f}mm"
            text_size, _ = cv2.getTextSize(box_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_w, text_h = text_size

            # Desenhar o fundo do texto
            cv2.rectangle(image, (x, y - text_h - 5), (x + text_w, y), (0, 255, 0), -1)
            # Colocar o texto na imagem
            cv2.putText(image, box_text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return measurements

# Captura da webcam
cap = cv2.VideoCapture(4)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Tentar detectar o tabuleiro
    found, corners = find_chessboard(frame, (GRID_ROWS - 1, GRID_COLS - 1))
    if found:
        # Refinar os cantos detectados
        corners = cv2.cornerSubPix(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), corners, (11, 11), (-1, -1),
                                   criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        # Desenhar o tabuleiro na imagem
        cv2.drawChessboardCorners(frame, (GRID_ROWS - 1, GRID_COLS - 1), corners, found)

        # Calcular a escala
        scale = calculate_scale(corners)

        if scale:
            cv2.putText(frame, f"Scale: {scale:.3f} mm/px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Medir os objetos na imagem automaticamente
            measurements = measure_object(frame, scale)

            for i, (w, h) in enumerate(measurements):
                print(f"Objeto {i + 1}: {w:.2f}mm x {h:.2f}mm")

    else:
        cv2.putText(frame, "Tabuleiro nao encontrado", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Medicao de Objetos", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
