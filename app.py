import streamlit as st
import sqlite3
from banco import criar_banco
from datetime import datetime
import os

criar_banco()

conn = sqlite3.connect("banco.db", check_same_thread=False)
cur = conn.cursor()

st.set_page_config(
    page_title="Portal Interno",
    layout="wide"
)

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

# LOGIN
if not st.session_state.logado:

    st.title("🏢 Portal da Empresa")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        cur.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND senha=?",
            (usuario, senha)
        )

        dados = cur.fetchone()

        if dados:
            st.session_state.logado = True
            st.session_state.admin = dados[3]
            st.session_state.usuario = usuario
            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")

# SISTEMA PRINCIPAL
else:

    menu = st.sidebar.radio(
        "Menu",
        ["Feed", "Agenda", "Admin"]
    )

    # ================= FEED =================
    if menu == "Feed":

        st.title("📢 Comunicados")

        cur.execute("""
        SELECT *
        FROM publicacoes
        ORDER BY id DESC
        """)
        posts = cur.fetchall()

        for post in posts:

            post_id = post[0]

            st.subheader(post[1])

            # IMAGEM
            if post[3]:
                caminho = os.path.join("uploads", post[3])

                if os.path.exists(caminho):
                    st.image(caminho)

            st.write(post[2])
            st.caption(post[4])

            # ================= CURTIDAS =================
            cur.execute(
                "SELECT COUNT(*) FROM curtidas WHERE post_id=?",
                (post_id,)
            )
            qtd_curtidas = cur.fetchone()[0]

            st.write(f"❤️ {qtd_curtidas} curtidas")

            if st.button(f"Curtir", key=f"curtir_{post_id}"):

                usuario = st.session_state.usuario

                cur.execute("""
                    SELECT * FROM curtidas
                    WHERE post_id=? AND usuario=?
                """, (post_id, usuario))

                ja_curtiu = cur.fetchone()

                if not ja_curtiu:
                    cur.execute("""
                        INSERT INTO curtidas (post_id, usuario)
                        VALUES (?,?)
                    """, (post_id, usuario))

                    conn.commit()
                    st.rerun()

            st.divider()

            # ================= COMENTÁRIO =================
            comentario = st.text_input(
                "Escreva um comentário",
                key=f"coment_input_{post_id}"
            )

            if st.button("Enviar comentário", key=f"coment_btn_{post_id}"):

                if comentario.strip():

                    cur.execute("""
                        INSERT INTO comentarios
                        (post_id, usuario, texto, data)
                        VALUES (?,?,?,?)
                    """, (
                        post_id,
                        st.session_state.usuario,
                        comentario,
                        datetime.now().strftime("%d/%m/%Y %H:%M")
                    ))

                    conn.commit()
                    st.rerun()

            # ================= LISTA DE COMENTÁRIOS =================
            cur.execute("""
                SELECT usuario, texto, data
                FROM comentarios
                WHERE post_id=?
                ORDER BY id DESC
            """, (post_id,))

            comentarios = cur.fetchall()

            for c in comentarios:
                st.markdown(f"**{c[0]}** ({c[2]})")
                st.write(c[1])

            st.divider()

    # ================= AGENDA =================
    elif menu == "Agenda":

        st.title("📅 Agenda")

        cur.execute("""
        SELECT *
        FROM eventos
        ORDER BY data
        """)

        eventos = cur.fetchall()

        for evento in eventos:
            st.write(f"📌 {evento[2]} - {evento[1]}")

    # ================= ADMIN =================
    elif menu == "Admin":

        if st.session_state.admin != 1:
            st.error("Sem permissão")
            st.stop()

        aba1, aba2 = st.tabs(["Nova Publicação", "Novo Evento"])

        # -------- PUBLICAÇÃO --------
        with aba1:

            titulo = st.text_input("Título")
            texto = st.text_area("Texto")
            imagem = st.file_uploader("Imagem", type=["jpg", "png", "jpeg"])

            if st.button("Publicar"):

                nome_arquivo = ""

                if imagem:

                    nome_arquivo = imagem.name

                    with open(
                        os.path.join("uploads", nome_arquivo),
                        "wb"
                    ) as f:
                        f.write(imagem.getbuffer())

                cur.execute("""
                    INSERT INTO publicacoes
                    (titulo,texto,imagem,data)
                    VALUES (?,?,?,?)
                """, (
                    titulo,
                    texto,
                    nome_arquivo,
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ))

                conn.commit()
                st.success("Publicação criada!")

        # -------- EVENTO --------
        with aba2:

            descricao = st.text_input("Descrição do Evento")
            data = st.date_input("Data")

            if st.button("Salvar Evento"):

                cur.execute("""
                    INSERT INTO eventos
                    (descricao,data)
                    VALUES (?,?)
                """, (
                    descricao,
                    str(data)
                ))

                conn.commit()
                st.success("Evento salvo!")