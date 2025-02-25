from flask import Flask, request, render_template_string, jsonify
import json
import logging
import hmac
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Secreto compartido con Mercado Pago (deberías obtenerlo de variables de entorno)
MP_SECRET = os.environ.get("MP_WEBHOOK_SECRET", "tu_clave_secreta")

# Lista para almacenar las últimas notificaciones recibidas (en memoria)
# En producción deberías usar una base de datos
notifications_history = []
MAX_HISTORY = 10

def verify_webhook_signature(request_data, signature, secret):
    """Verifica la firma del webhook de Mercado Pago"""
    if not signature:
        return False
    
    calculated_signature = hmac.new(
        secret.encode('utf-8'),
        request_data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_signature, signature)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Obtener los datos crudos y la firma
        request_data = request.get_data()
        signature = request.headers.get('X-Signature')
        
        # Verificar la firma (esto dependerá de cómo Mercado Pago implementa la verificación)
        # Nota: Ajusta esto según la documentación específica de Mercado Pago
        # if not verify_webhook_signature(request_data, signature, MP_SECRET):
        #     logging.warning("Firma de webhook inválida")
        #     return jsonify({"error": "Firma inválida"}), 403
        
        # Obtener los datos JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos JSON no encontrados"}), 400
            
        # Registrar la notificación recibida
        logging.info(f"Webhook recibido: {json.dumps(data)[:100]}...")
        
        # Guardar la notificación en el historial
        notification_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data,
            "headers": dict(request.headers)
        }
        notifications_history.insert(0, notification_entry)
        
        # Mantener solo las últimas MAX_HISTORY notificaciones
        if len(notifications_history) > MAX_HISTORY:
            notifications_history.pop()
        
        # Procesar según el tipo de notificación
        notification_type = data.get('type')
        if notification_type == 'payment':
            # Procesar un pago
            payment_data = data.get('data', {})
            # Aquí implementarías tu lógica de negocio para procesar el pago
            logging.info(f"Pago procesado: ID {payment_data.get('id')}")
        elif notification_type == 'transfer':
            # Procesar una transferencia
            transfer_data = data.get('data', {})
            # Aquí implementarías tu lógica para procesar la transferencia
            logging.info(f"Transferencia procesada: ID {transfer_data.get('id')}")
        
        # Devolver respuesta de éxito
        return jsonify({"status": "success", "message": "Notificación procesada correctamente"})
        
    except Exception as e:
        logging.error(f"Error procesando webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/webhook/view", methods=["GET"])
def webhook_view():
    """Página para visualizar las notificaciones recibidas en tarjetas simples"""
    return render_template_string("""
        <html>
            <head>
                <title>Monitor de Webhook Mercado Pago</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { box-sizing: border-box; }
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        background-color: #f5f5f5; 
                    }
                    h1 { 
                        color: #2d3748; 
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                    }
                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 20px;
                    }
                    .refresh-btn {
                        padding: 8px 15px;
                        background: #4361ee;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .refresh-btn:hover {
                        background: #3a56d4;
                    }
                    .card-container {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                        gap: 20px;
                    }
                    .card {
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        padding: 15px;
                        transition: transform 0.3s ease;
                    }
                    .card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    }
                    .card-header {
                        border-bottom: 1px solid #eee;
                        padding-bottom: 10px;
                        margin-bottom: 15px;
                    }
                    .timestamp {
                        font-size: 0.8em;
                        color: #6c757d;
                    }
                    .notification-type {
                        display: inline-block;
                        padding: 3px 8px;
                        border-radius: 15px;
                        font-size: 0.8em;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }
                    .type-payment {
                        background: #d4edda;
                        color: #155724;
                    }
                    .type-transfer {
                        background: #cce5ff;
                        color: #004085;
                    }
                    .type-other {
                        background: #f8d7da;
                        color: #721c24;
                    }
                    .card-body {
                        margin-bottom: 15px;
                    }
                    .card-details {
                        font-size: 0.9em;
                        margin-top: 5px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                    .detail-label {
                        font-weight: bold;
                        margin-right: 5px;
                    }
                    .empty-state {
                        text-align: center;
                        padding: 50px 20px;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    .view-json-btn {
                        display: block;
                        text-align: center;
                        padding: 5px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        color: #495057;
                        text-decoration: none;
                        margin-top: 10px;
                        cursor: pointer;
                    }
                    .view-json-btn:hover {
                        background: #e9ecef;
                    }
                    .modal {
                        display: none;
                        position: fixed;
                        z-index: 1;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        overflow: auto;
                        background-color: rgba(0,0,0,0.4);
                    }
                    .modal-content {
                        background-color: #fefefe;
                        margin: 10% auto;
                        padding: 20px;
                        border: 1px solid #888;
                        border-radius: 8px;
                        width: 80%;
                        max-width: 800px;
                    }
                    .close {
                        color: #aaa;
                        float: right;
                        font-size: 28px;
                        font-weight: bold;
                    }
                    .close:hover,
                    .close:focus {
                        color: black;
                        text-decoration: none;
                        cursor: pointer;
                    }
                    pre {
                        background: #f8f9fa;
                        padding: 10px;
                        border-radius: 4px;
                        overflow-x: auto;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Monitor de Webhook - Mercado Pago</h1>
                        <button class="refresh-btn" onclick="location.reload()">Actualizar</button>
                    </div>
                    
                    {% if notifications %}
                        <div class="card-container">
                            {% for notification in notifications %}
                                <div class="card">
                                    <div class="card-header">
                                        <div class="timestamp">{{ notification.timestamp }}</div>
                                        {% set type = notification.data.get('type', 'desconocido') %}
                                        <div class="notification-type 
                                            {% if type == 'payment' %}type-payment
                                            {% elif type == 'transfer' %}type-transfer
                                            {% else %}type-other{% endif %}">
                                            Tipo: {{ type }}
                                        </div>
                                    </div>
                                    <div class="card-body">
                                        {% if notification.data.get('data') %}
                                            {% if notification.data.data.get('id') %}
                                                <div class="card-details">
                                                    <span class="detail-label">ID:</span>
                                                    {{ notification.data.data.id }}
                                                </div>
                                            {% endif %}
                                            
                                            {% if notification.data.data.get('amount') %}
                                                <div class="card-details">
                                                    <span class="detail-label">Monto:</span>
                                                    {{ notification.data.data.amount }}
                                                    {% if notification.data.data.get('currency') %}
                                                        {{ notification.data.data.currency }}
                                                    {% endif %}
                                                </div>
                                            {% endif %}
                                            
                                            {% if notification.data.data.get('status') %}
                                                <div class="card-details">
                                                    <span class="detail-label">Estado:</span>
                                                    {{ notification.data.data.status }}
                                                </div>
                                            {% endif %}
                                            
                                            {% if notification.data.data.get('description') %}
                                                <div class="card-details">
                                                    <span class="detail-label">Descripción:</span>
                                                    {{ notification.data.data.description }}
                                                </div>
                                            {% endif %}
                                        {% endif %}
                                        
                                        {% if notification.data.get('action') %}
                                            <div class="card-details">
                                                <span class="detail-label">Acción:</span>
                                                {{ notification.data.action }}
                                            </div>
                                        {% endif %}
                                    </div>
                                    <button class="view-json-btn" onclick="showJson({{ loop.index0 }})">Ver JSON completo</button>
                                </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <div class="empty-state">
                            <h2>No se han recibido notificaciones</h2>
                            <p>Las notificaciones aparecerán aquí cuando Mercado Pago envíe datos a tu webhook.</p>
                        </div>
                    {% endif %}
                </div>
                
                <!-- Modal para mostrar JSON -->
                <div id="jsonModal" class="modal">
                    <div class="modal-content">
                        <span class="close" onclick="closeModal()">&times;</span>
                        <h2 id="modal-title">Detalles completos</h2>
                        <pre id="json-content"></pre>
                    </div>
                </div>
                
                <script>
                    // Almacenar los datos JSON para cada notificación
                    const notificationsData = [
                        {% for notification in notifications %}
                            {{ notification.data|tojson }},
                        {% endfor %}
                    ];
                    
                    // Funciones para el modal
                    const modal = document.getElementById("jsonModal");
                    const jsonContent = document.getElementById("json-content");
                    const modalTitle = document.getElementById("modal-title");
                    
                    function showJson(index) {
                        const data = notificationsData[index];
                        jsonContent.textContent = JSON.stringify(data, null, 2);
                        modal.style.display = "block";
                    }
                    
                    function closeModal() {
                        modal.style.display = "none";
                    }
                    
                    // Cerrar modal al hacer clic fuera de él
                    window.onclick = function(event) {
                        if (event.target == modal) {
                            closeModal();
                        }
                    }
                </script>
            </body>
        </html>
    """, notifications=notifications_history)

@app.route("/", methods=["GET"])
def home():
    """Página de inicio con información sobre el servicio"""
    return render_template_string("""
        <html>
            <head>
                <title>Webhook para Mercado Pago</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px; 
                        background-color: #f5f5f5;
                    }
                    h1 { color: #2d3748; text-align: center; }
                    .card { 
                        background: #fff; 
                        border-radius: 8px; 
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1); 
                        padding: 20px; 
                        margin-bottom: 20px; 
                    }
                    .btn {
                        display: inline-block;
                        padding: 10px 15px;
                        background: #4361ee;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-right: 10px;
                    }
                    .btn:hover {
                        background: #3a56d4;
                    }
                    .status-badge {
                        display: inline-block;
                        padding: 5px 10px;
                        background: #d4edda;
                        color: #155724;
                        border-radius: 15px;
                        font-size: 0.9em;
                        font-weight: bold;
                    }
                    code {
                        background: #f1f3f5;
                        padding: 2px 5px;
                        border-radius: 3px;
                        font-size: 0.9em;
                    }
                    pre {
                        background: #f8f9fa;
                        padding: 10px;
                        border-radius: 4px;
                        overflow-x: auto;
                    }
                </style>
            </head>
            <body>
                <h1>Servicio de Webhook para Mercado Pago</h1>
                
                <div class="card">
                    <h2>Estado</h2>
                    <p><span class="status-badge">✅ Activo</span> El servicio está funcionando correctamente.</p>
                    <a href="/webhook/view" class="btn">Ver notificaciones</a>
                </div>
                
                <div class="card">
                    <h2>Información del servicio</h2>
                    <p>Este servicio está configurado para recibir notificaciones de Mercado Pago a través de webhooks.</p>
                    <ul>
                        <li><strong>URL del webhook:</strong> <code>{{ request.host_url }}webhook</code></li>
                        <li><strong>Monitor de notificaciones:</strong> <code>{{ request.host_url }}webhook/view</code></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Cómo probar</h2>
                    <p>Para enviar una notificación de prueba al webhook, puedes usar cURL:</p>
                    <pre>curl -X POST {{ request.host_url }}webhook \
-H "Content-Type: application/json" \
-d '{"type":"transfer","data":{"id":"12345","amount":1000}}'</pre>
                </div>
            </body>
        </html>
    """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)