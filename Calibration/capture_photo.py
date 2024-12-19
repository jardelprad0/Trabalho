import cv2
import os

# Defina o caminho da pasta onde as fotos serão salvas
pasta_destino = "/home/jardel/Desktop/Trabalho/Calibration/c920"

# Cria a pasta se ela não existir
os.makedirs(pasta_destino, exist_ok=True)

# Inicializa a webcam (0 é geralmente o índice da webcam padrão)
camera = cv2.VideoCapture(4)

if not camera.isOpened():
    print("Erro ao acessar a webcam.")
    exit()

print("Pressione 'Espaço' para tirar uma foto, 'ESC' para sair.")

foto_id = 1  # Contador para nomear as fotos

while True:
    # Captura o frame da webcam
    ret, frame = camera.read()
    if not ret:
        print("Falha ao capturar a imagem.")
        break

    # Exibe o frame na janela
    cv2.imshow("Webcam", frame)

    # Aguarda uma tecla pressionada
    key = cv2.waitKey(1)

    if key == 27:  # ESC para sair
        print("Saindo...")
        break
    elif key == 32:  # Espaço para capturar uma foto
        # Gera o caminho completo para salvar a foto
        filename = os.path.join(pasta_destino, f"foto_{foto_id}.jpg")
        # Salva a imagem
        cv2.imwrite(filename, frame)
        print(f"Foto {foto_id} capturada e salva em: {filename}")
        foto_id += 1  # Incrementa o contador

# Libera a câmera e fecha as janelas
camera.release()
cv2.destroyAllWindows()
