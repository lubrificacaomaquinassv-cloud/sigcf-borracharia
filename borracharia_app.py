import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
from supabase import create_client

st.set_page_config(
    page_title="Borracharia SV - SIGCF",
    page_icon="🛞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from sigcf_auth import exigir_acesso, logo_html

TIPOS_MANUT = ["REMENDO", "RODÍZIO", "TROCA DE PNEU", "TROCA DE CÂMARA"]

exigir_acesso("Gestão de Borracharia")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');
[data-testid="stAppViewContainer"]{background:#0a1409;}
[data-testid="stSidebar"]{background:#111c10;border-right:1px solid #1e2e1c;}
[data-testid="stHeader"]{background:#0a1409;}
[data-testid="stSidebar"]{display:none;}
h1,h2,h3,h4,p,span,label{color:#e8edd0;}
h1{font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stCaption,[data-testid="stCaptionContainer"] p{color:#8aab80!important;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#8aab80;
 border-left:4px solid #4a9e3f;padding-left:10px;margin:8px 0 12px;}
.logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;
 border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}
.logo-frame img{display:block;border-radius:8px;}
.ctx-box{background:#0d180c;border:1px solid #1e2e1c;border-radius:12px;padding:14px 16px;margin-bottom:12px;}
.cat-badge{display:inline-block;background:#0d180c;border:1px solid #4a9e3f;color:#6fcf60;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1px;
 padding:4px 12px;border-radius:8px;font-size:13px;}
.cat-badge.pendente{border-color:#c9a227;color:#e8c547;}

.stTextInput input,.stNumberInput input,.stTextArea textarea,
[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input{
 background:#dce6d2!important;color:#1a2818!important;
 border:1px solid #4a6644!important;border-radius:8px!important;}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus,
[data-testid="stDateInput"] input:focus,[data-testid="stTimeInput"] input:focus{
 border-color:#6fcf60!important;box-shadow:0 0 0 1px #6fcf6044!important;}
div[data-baseweb="select"] > div{
 background:#dce6d2!important;border:1px solid #4a6644!important;
 color:#1a2818!important;border-radius:8px!important;}
div[data-baseweb="select"] div{color:#1a2818!important;}
div[data-baseweb="select"] svg{fill:#4a6644!important;}
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"] ul{background:#e8edd0!important;}
div[data-baseweb="popover"] li{color:#1a2818!important;}
[data-testid="stNumberInput"] button{
 background:#cdd9c4!important;border-color:#4a6644!important;color:#1a2818!important;}
[data-testid="stForm"]{
 background:#0d180c!important;border:1px solid #1e2e1c!important;
 border-radius:12px;padding:12px 16px;}
[data-testid="stVerticalBlockBorderWrapper"]{
 background:#0d180c!important;border-color:#1e2e1c!important;}
div[data-testid="stMetric"]{background:#0d180c;border:1px solid #1e2e1c;border-radius:10px;padding:10px 14px;}
div[data-testid="stMetric"] label{color:#8aab80!important;}
div[data-testid="stMetricValue"]{color:#6fcf60!important;font-family:'Barlow Condensed',sans-serif;}
.stTabs [data-baseweb="tab-list"]{background:#0d180c;border-bottom:1px solid #1e2e1c;gap:8px;}
.stTabs [data-baseweb="tab"]{
 color:#8aab80!important;font-family:'Barlow Condensed',sans-serif;
 font-weight:600;letter-spacing:0.5px;}
.stTabs [aria-selected="true"]{
 color:#e8edd0!important;border-bottom-color:#4a9e3f!important;}
.stTabs [data-baseweb="tab-highlight"]{background-color:#4a9e3f!important;}
[data-testid="stExpander"]{
 background:#0d180c!important;border:1px solid #1e2e1c!important;border-radius:10px;}
[data-testid="stExpander"] summary{color:#e8edd0!important;}
[data-testid="stRadio"] label span{color:#e8edd0!important;}
.stButton button,[data-testid="stFormSubmitButton"] button{
 background:#4a9e3f!important;color:#ffffff!important;border:1px solid #6fcf60!important;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1.5px;
 text-transform:uppercase;border-radius:8px;}
.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{background:#3d8534!important;}
.stButton button p,[data-testid="stFormSubmitButton"] button p{color:#ffffff!important;}
</style>
""", unsafe_allow_html=True)


def dark_table(df, height=320):
    if df.empty:
        st.info("Nenhum registro.")
        return
    rows = "".join(
        "<tr>" + "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #1e2e1c;'
            f'color:#e8edd0;font-size:12px;white-space:nowrap;">{v}</td>'
            for v in row) + "</tr>"
        for _, row in df.iterrows())
    headers = "".join(
        f'<th style="padding:7px 10px;background:#111c10;color:#8aab80;font-size:10px;'
        f'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
        f'border-bottom:2px solid #1e2e1c;white-space:nowrap;">{c}</th>'
        for c in df.columns)
    st.markdown(
        f'<div style="overflow-x:auto;border:1px solid #1e2e1c;border-radius:10px;">'
        f'<div style="max-height:{height}px;overflow-y:auto;">'
        f'<table style="width:100%;border-collapse:collapse;background:#0d180c;'
        f'font-family:Barlow Condensed,sans-serif;"><thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


def gerar_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as exc:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY nos Secrets do Streamlit Cloud.")
    st.caption(str(exc))
    st.stop()


@st.cache_data(ttl=60)
def carregar_frota():
    res = (
        supabase.table("dim_frota")
        .select("id_frota, modelo")
        .eq("ativo", True)
        .order("id_frota")
        .execute()
    )
    return res.data or []


@st.cache_data(ttl=10)
def carregar_os(limit=100):
    try:
        res = (
            supabase.table("os_borracharia")
            .select("*")
            .order("criado_em", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


@st.cache_data(ttl=300)
def carregar_borracheiros():
    res = (
        supabase.table("dim_colaborador")
        .select("nome")
        .eq("ativo", True)
        .order("nome")
        .execute()
    )
    return [r["nome"] for r in (res.data or [])]


def proximo_numero_os(os_data: list) -> int:
    nums = []
    for o in os_data:
        n = str(o.get("numero_os", ""))
        if n.startswith("BOR-"):
            try:
                nums.append(int(n.replace("BOR-", "")))
            except ValueError:
                pass
    return (max(nums) + 1) if nums else 1


def os_para_df(rows: list) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    cols = {
        "numero_os": "O.S.",
        "id_frota": "Frota",
        "borracheiro": "Borracheiro",
        "tipo_manutencao": "Tipo",
        "horimetro": "Hor/KM",
        "tempo_minutos": "Min",
        "status": "Status",
        "descricao": "Descrição",
    }
    exist = [c for c in cols if c in df.columns]
    out = df[exist].rename(columns=cols)
    if "Min" in out.columns:
        out["Min"] = out["Min"].apply(lambda v: f"{int(v)} min" if pd.notna(v) and v else "—")
    return out


frota_data = carregar_frota()
os_data = carregar_os()
borracheiros = carregar_borracheiros()
lista_frotas = [f"{f['id_frota']} - {f['modelo']}" for f in frota_data] or ["Cadastre a frota"]
lista_borracheiros = borracheiros or ["Cadastre o borracheiro"]
num_os = proximo_numero_os(os_data)
numero_os_str = f"BOR-{num_os:04d}"

col_logo, col_titulo, col_acao = st.columns([1.1, 5, 1])
with col_logo:
    st.markdown(logo_html(118), unsafe_allow_html=True)
with col_titulo:
    st.title("Gestão de Borracharia")
    st.caption("SIGCF — Ordem de serviço de borracharia · vínculo frota → painel financeiro")
with col_acao:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()

st.divider()

tab_nova, tab_consulta = st.tabs(["📝 Nova O.S.", "📋 Consultar O.S."])

with tab_nova:
    st.markdown('<div class="sec">Registrar ordem de serviço</div>', unsafe_allow_html=True)
    st.markdown('<div class="ctx-box">', unsafe_allow_html=True)

    cf1, cf2 = st.columns([3, 1])
    with cf1:
        frota_sel = st.selectbox("🚜 Equipamento (dim_frota)", options=lista_frotas, key="bor_frota")
    with cf2:
        id_frota = frota_sel.split(" - ")[0].strip() if " - " in frota_sel else frota_sel
        st.markdown(
            f'<div style="background:#111c10;border:1px solid #1e2e1c;border-radius:10px;'
            f'padding:12px 14px;text-align:center;margin-top:28px;">'
            f'<p style="margin:0;color:#8aab80;font-size:11px;text-transform:uppercase;'
            f'letter-spacing:1px;">Frota selecionada</p>'
            f'<p style="margin:4px 0 0;color:#e8edd0;font-size:28px;font-weight:700;'
            f'font-family:Barlow Condensed,sans-serif;">{id_frota}</p></div>',
            unsafe_allow_html=True,
        )

    with st.form("form_borracharia", clear_on_submit=True):
        st.metric("🔖 O.S. atual", numero_os_str)

        c1, c2 = st.columns(2)
        with c1:
            borracheiro = st.selectbox("👤 Borracheiro", options=lista_borracheiros)
            tipo_manut = st.selectbox("🔧 Tipo de manutenção", options=TIPOS_MANUT)
            horimetro = st.number_input("⏱️ Horímetro ou KM atual", min_value=0.0, step=0.1, format="%.1f")
        with c2:
            hora_entrada = st.time_input("🕐 Hora entrada", value=None)
            hora_saida = st.time_input("🕑 Hora saída", value=None)
            status_os = st.radio("Status", ["FINALIZADO", "PENDENTE"], horizontal=True)

        descricao = st.text_area("📝 Descrição do serviço e peças aplicadas", max_chars=300)
        observacao = st.text_area("💬 Observação", max_chars=200)

        enviar = st.form_submit_button("✅ Salvar O.S.", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if enviar:
        if not descricao.strip():
            st.warning("Descrição é obrigatória.")
        else:
            tempo_min = None
            if hora_entrada and hora_saida:
                dt_e = datetime.combine(date.today(), hora_entrada)
                dt_s = datetime.combine(date.today(), hora_saida)
                if dt_s > dt_e:
                    tempo_min = int((dt_s - dt_e).total_seconds() / 60)

            novo = {
                "numero_os": numero_os_str,
                "id_frota": id_frota,
                "horimetro": str(horimetro),
                "borracheiro": borracheiro,
                "tipo_manutencao": tipo_manut,
                "hora_entrada": str(hora_entrada) if hora_entrada else None,
                "hora_saida": str(hora_saida) if hora_saida else None,
                "tempo_minutos": tempo_min,
                "status": status_os,
                "descricao": descricao.strip(),
                "observacao": observacao.strip() or None,
                "criado_em": datetime.now().isoformat(),
            }
            try:
                supabase.table("os_borracharia").insert(novo).execute()
                msg = f"O.S. {numero_os_str} registrada!"
                if tempo_min:
                    msg += f" Tempo: {tempo_min} min."
                st.success(msg)
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

with tab_consulta:
    st.markdown('<div class="sec">Consultar ordens de serviço</div>', unsafe_allow_html=True)
    os_data = carregar_os(100)
    if not os_data:
        st.info("Nenhum serviço registrado.")
    else:
        df = os_para_df(os_data)
        pendentes = sum(1 for o in os_data if o.get("status") == "PENDENTE")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total O.S.", len(os_data))
        m2.metric("Pendentes", pendentes)
        m3.metric("Finalizadas", len(os_data) - pendentes)
        dark_table(df, height=400)
        st.download_button(
            "⬇️ Exportar Excel",
            data=gerar_excel(df),
            file_name=f"borracharia_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

st.divider()
st.markdown('<div class="sec">Últimos serviços</div>', unsafe_allow_html=True)
dark_table(os_para_df(os_data[:12]), height=200)
st.caption("SIGCF | Borracharia SV | Núcleo de Controladoria SV")
