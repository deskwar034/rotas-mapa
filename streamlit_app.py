import streamlit as st
import googlemaps
import urllib.parse

# Configuração da página
st.set_page_config(page_title="Otimizador de Rotas", page_icon="🗺️", layout="centered")

st.title("🗺️ Otimizador de Rotas para Google Maps")
st.markdown("Insira os endereços para calcular a rota mais rápida e gerar o link direto para o navegador ou celular.")

# Configuração da API via Senha
st.sidebar.header("Acesso")
senha_input = st.sidebar.text_input("Senha de Acesso", type="password", 
                                help="Digite a senha para ativar a API do Google Maps automaticamente.")

# Lógica para carregar a API Key a partir do secret, caso a senha esteja correta
api_key = None
if senha_input:
    try:
        if senha_input == st.secrets["SENHA"]:
            api_key = st.secrets["API_MAPS"]
            st.sidebar.success("✅ Acesso liberado!")
        else:
            st.sidebar.error("❌ Senha incorreta.")
    except KeyError:
        st.sidebar.error("⚠️ Erro: Os secrets 'SENHA' e 'API_MAPS' não foram configurados corretamente no Streamlit.")

# Inputs do Usuário
st.subheader("Defina o Trajeto")
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("Ponto de Partida", placeholder="Ex: Quartel 1º GBM, Campo Grande - MS")
with col2:
    destination = st.text_input("Ponto Final", placeholder="Ex: Av. Afonso Pena, Campo Grande - MS")

st.markdown("**Paradas Intermediárias (Uma por linha):**")
waypoints_text = st.text_area("Endereços", height=150, 
                              placeholder="Rua 14 de Julho, Campo Grande - MS\nAv. Mato Grosso, Campo Grande - MS")

if st.button("Calcular Melhor Rota", type="primary"):
    if not api_key:
        st.error("Por favor, insira a senha correta no menu lateral para habilitar a API.")
    elif not origin or not destination or not waypoints_text:
        st.warning("Preencha o ponto de partida, o destino e pelo menos uma parada intermediária.")
    else:
        # Limpa e organiza a lista de endereços
        waypoints = [addr.strip() for addr in waypoints_text.split('\n') if addr.strip()]
        
        # A URL do Maps suporta até um certo limite de caracteres, e a API limita a 25 paradas.
        if len(waypoints) > 25:
            st.error("O limite máximo da API do Google para otimização é de 25 paradas.")
        else:
            try:
                with st.spinner("Calculando e otimizando a rota..."):
                    # Inicializa o cliente do Google Maps
                    gmaps = googlemaps.Client(key=api_key)
                    
                    # Faz a requisição pedindo otimização (optimize_waypoints=True)
                    directions = gmaps.directions(
                        origin,
                        destination,
                        waypoints=waypoints,
                        optimize_waypoints=True
                    )
                    
                    if directions:
                        route = directions[0]
                        waypoint_order = route['waypoint_order']
                        
                        # Reordena a lista original do usuário com base na resposta da API
                        optimized_waypoints = [waypoints[i] for i in waypoint_order]
                        
                        st.success("✅ Rota otimizada com sucesso!")
                        
                        # Mostra a nova ordem na tela
                        st.markdown("### Melhor Ordem de Paradas:")
                        for i, wp in enumerate(optimized_waypoints, 1):
                            st.write(f"**{i}.** {wp}")
                            
                        # Monta a URL Universal do Google Maps (Maps URLs)
                        safe_origin = urllib.parse.quote(origin)
                        safe_destination = urllib.parse.quote(destination)
                        
                        # O Google Maps URL espera as paradas separadas por "|"
                        safe_waypoints = urllib.parse.quote("|".join(optimized_waypoints))
                        
                        # URL corrigida para o formato padrão do Google Maps Directions
                        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={safe_origin}&destination={safe_destination}&waypoints={safe_waypoints}"
                        
                        st.divider()
                        st.markdown(f"### [📍 Clique aqui para abrir a rota no Google Maps]({maps_url})")
                    else:
                        st.error("O Google não conseguiu traçar uma rota com os endereços fornecidos. Verifique a grafia.")
                        
            except Exception as e:
                st.error(f"Erro ao processar a API: {e}")
