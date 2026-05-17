from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://azhpxhrwhegfysoeqmft.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6aHB4aHJ3aGVnZnlzb2VxbWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NzUxODcsImV4cCI6MjA5NDI1MTE4N30.iQU1T1NLaGIQyqScLS6qNaoo1QWcI8Mh-jjN52TU5to"
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return send_from_directory('.', 'borracharia_sv.html')

@app.route('/api/bor', methods=['POST'])
def salvar_os():
    data = request.json
    from datetime import datetime
    he = data.get('hora_entrada')
    hs = data.get('hora_saida')
    tempo = None
    if he and hs:
        try:
            fmt = "%Y-%m-%dT%H:%M"
            tempo = int((datetime.strptime(hs, fmt) - datetime.strptime(he, fmt)).total_seconds() / 60)
        except Exception:
            tempo = None

    payload = {
        "numero_os":       data.get("numero_os"),
        "id_frota":        data.get("id_frota"),
        "horimetro":       data.get("horimetro"),
        "borracheiro":     data.get("borracheiro"),
        "tipo_manutencao": data.get("tipo_manutencao"),
        "hora_entrada":    he,
        "hora_saida":      hs,
        "tempo_minutos":   tempo,
        "Status":          data.get("status"),
        "descrição":       data.get("descricao"),
        "Observação":      data.get("observacao"),
    }

    sb.table('os_borracharia').insert(payload).execute()
    return jsonify({"ok": True})

@app.route('/api/bor/ultimas', methods=['GET'])
def ultimas_os():
    res = (sb.table('os_borracharia')
             .select('numero_os, id_frota, borracheiro, Status')
             .order('criado_em', desc=True)
             .limit(5)
             .execute())
    # normaliza a chave Status para status no retorno
    rows = []
    for r in res.data:
        rows.append({
            "numero_os":  r.get("numero_os"),
            "id_frota":   r.get("id_frota"),
            "borracheiro": r.get("borracheiro"),
            "status":     r.get("Status")
        })
    return jsonify(rows)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
