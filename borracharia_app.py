import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
 
st.set_page_config(page_title="Borracharia SV - SIGCF", layout="wide")
 
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=110)
with col_titulo:
    st.title("Gestao de Borracharia - SV")
    st.caption("SIGCF - Sistema Integrado de Gestao de Custos de Frota")
 
st.divider()
 
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
 
@st.cache_data(ttl=60)
def carregar_frota():
    res = supabase.table("dim_frota").select("id_frota, modelo").eq("ativo", True).order("modelo").execute()
    return res.data or []
 
@st.cache_data(ttl=10)
def carregar_os():
    try:
        res = (supabase.table("os_borracharia")
               .select("numero_os, id_frota, borracheiro, status, criado_em")
               .order("criado_em", desc=True)
               .limit(50)
               .execute())
        return res.data or []
    except Exception:
        return []
 
@st.cache_data(ttl=300)
def carregar_borracheiros():
    res = supabase.table("dim_colaborador").select("id_colaborador, nome").eq("ativo", True).order("nome").execute()
    return res.data or []
 
frota_data         = carregar_frota()
os_data            = carregar_os()
borracheiros_data  = carregar_borracheiros()
 
lista_frotas       = [f"{f['id_frota']} - {f['modelo']}" for f in frota_data] or ["Cadastre a frota"]
lista_borracheiros = [m['nome'] for m in borracheiros_data] or ["Cadastre o borracheiro"]
 
proximo_numero = 1
if os_data:
    numeros = [int(o['numero_os'].replace('BOR-','')) for o in os_data if o.get('numero_os','').startswith('BOR-')]
    if numeros:
        proximo_numero = max(numeros) + 1
 
with st.sidebar:
    st.image("https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg", width=140)
    st.divider()
    st.header("Ultimos Servicos")
    if os_data:
        df_os = pd.DataFrame(os_data)[['numero_os','id_frota','borracheiro','status']].head(5)
        st.table(df_os)
    else:
        st.info("Nenhum servico registrado.")
 
with st.form("form_borracharia", clear_on_submit=True):
    col_os, _ = st.columns([1, 3])
    with col_os:
        st.metric("O.S. ATUAL", f"BOR-{proximo_numero:04d}")
 
    c1, c2 = st.columns(2)
 
    with c1:
        frota_sel   = st.selectbox("Selecione o Equipamento", options=lista_frotas)
        borracheiro = st.selectbox("Borracheiro", options=lista_borracheiros)
        tipo_manut  = st.selectbox("Tipo de Manutencao", [
            "REMENDO", "RODIZIO", "TROCA DE PNEU", "TROCA DE CAMARA"
        ])
 
    with c2:
        horimetro    = st.number_input("Horimetro ou KM Atual", min_value=0.0, step=0.1, format="%.1f")
        hora_entrada = st.time_input("Hora Entrada", value=None)
        hora_saida   = st.time_input("Hora Saida", value=None)
        status_os    = st.radio("Status", ["FINALIZADO", "PENDENTE"], horizontal=True)
 
    descricao  = st.text_area("Descricao do servico e pecas aplicadas", max_chars=300)
    observacao = st.text_area("Observacao", max_chars=200)
 
    enviar = st.form_submit_button("SALVAR NO SISTEMA")
 
    if enviar:
        if not descricao.strip():
            st.warning("Descricao e obrigatoria.")
        else:
            tempo_min = None
            if hora_entrada and hora_saida:
                dt_e = datetime.combine(datetime.today(), hora_entrada)
                dt_s = datetime.combine(datetime.today(), hora_saida)
                if dt_s > dt_e:
                    tempo_min = int((dt_s - dt_e).total_seconds() / 60)
 
            id_frota = frota_sel.split(" - ")[0].strip()
 
            novo = {
                "numero_os":       f"BOR-{proximo_numero:04d}",
                "id_frota":        id_frota,
                "horimetro":       str(horimetro),
                "borracheiro":     borracheiro,
                "tipo_manutencao": tipo_manut,
                "hora_entrada":    str(hora_entrada) if hora_entrada else None,
                "hora_saida":      str(hora_saida)   if hora_saida   else None,
                "tempo_minutos":   tempo_min,
                "status":          status_os,
                "descricao":       descricao,
                "observacao":      observacao,
                "criado_em":       datetime.now().isoformat()
            }
 
            try:
                supabase.table("os_borracharia").insert(novo).execute()
                st.success(
                    f"O.S. BOR-{proximo_numero:04d} registrada! Tempo: {tempo_min} min"
                    if tempo_min else
                    f"O.S. BOR-{proximo_numero:04d} registrada!"
                )
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
 
st.divider()
st.caption("SIGCF | Borracharia SV | Nucleo de Controladoria SV")
