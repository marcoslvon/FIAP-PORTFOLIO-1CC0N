"""
NEIGHBORHOOD ACTION DASHBOARD
Painel comunitário de ocorrências de um bairro simulado.

Global Solution 2026.2 - FIAP - case CitizenTech

Para executar (a partir da pasta do projeto):
    python src/sistema.py

Usa apenas Python básico: listas, dicionários, filas, pilhas, matrizes,
condicionais, laços e funções. Nenhuma biblioteca externa é necessária.
"""


# ============================================================
# SEÇÃO 1 - CONSTANTES E VALORES PADRONIZADOS
# ============================================================

BAIRRO = "Jardim das Acácias"

# Dia simulado em que o sistema está sendo usado.
# Os dados do bairro vão do dia 1 ao dia 23, então "hoje" é o dia 25.
DIA_ATUAL = 25

# Valores padronizados: dentro do sistema as categorias e as situações
# são sempre escritas em letras minúsculas e sem acento. Isso evita que
# "Iluminação", "iluminacao" e "ILUMINACAO" virem três coisas diferentes.
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
SITUACOES = ["aberta", "em_analise", "concluida"]

# Nomes "bonitos" usados só na hora de mostrar na tela.
NOME_CATEGORIA = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação"
}

NOME_SITUACAO = {
    "aberta": "Aberta",
    "em_analise": "Em análise",
    "concluida": "Concluída"
}

# Significado de cada situação (exigido pelo enunciado).
SIGNIFICADO_SITUACAO = {
    "aberta": "Registrada pelo morador e ainda não examinada pela equipe",
    "em_analise": "Já passou pela triagem e está sendo avaliada",
    "concluida": "Demanda encerrada no painel da comunidade"
}

# Campos que toda ocorrência precisa ter preenchidos.
CAMPOS_OBRIGATORIOS = ["id", "categoria", "descricao", "local",
                       "dia_abertura", "status"]


# ============================================================
# SEÇÃO 2 - ESTRUTURAS DE DADOS DO SISTEMA
# ============================================================

# LISTA: guarda todas as ocorrências válidas, na ordem em que foram lidas.
ocorrencias = []

# DICIONÁRIO: permite achar uma ocorrência direto pelo código,
# sem precisar percorrer a lista inteira.
indice_por_id = {}

# FILA (FIFO - o primeiro que entra é o primeiro que sai):
# guarda os códigos das ocorrências ainda abertas, na ordem de registro.
fila_analise = []

# PILHA (LIFO - o último que entra é o primeiro que sai):
# guarda o histórico de atualizações. O topo é sempre a mudança mais recente.
pilha_historico = []

# Lista dos registros que foram recusados pela validação.
registros_rejeitados = []

# Quantas linhas de dados foram lidas no total (para o painel).
total_linhas_lidas = 0


# Cópia dos dados usada apenas se o arquivo CSV não for encontrado.
# Tem exatamente o mesmo formato do arquivo dados/ocorrencias.csv.
LINHAS_RESERVA = [
    "id;categoria;descricao;local;dia_abertura;status;dia_conclusao",
    "OC-001;iluminacao;Poste apagado em frente ao coreto;Praça Central;2;concluida;9",
    "OC-002;limpeza;Acúmulo de lixo na calçada;Rua das Palmeiras;3;aberta;",
    "OC-003;acessibilidade;Rampa de acesso danificada;Posto de Saúde;3;em_analise;",
    "OC-004;conservacao;Banco de madeira quebrado;Parque do Bairro;5;aberta;",
    "OC-005;iluminacao;Lâmpadas piscando durante a noite;Avenida Principal;6;em_analise;",
    "OC-006;limpeza;Bueiro entupido com folhas;Rua das Oliveiras;7;concluida;12",
    "OC-007;acessibilidade;Ponto de ônibus sem piso tátil;Terminal de Ônibus;8;aberta;",
    "OC-008;conservacao;Pintura da quadra desgastada;Quadra Esportiva;10;aberta;",
    "OC-009;iluminacao;Refletor da quadra queimado;Quadra Esportiva;11;em_analise;",
    "OC-010;limpeza;Entulho acumulado em terreno baldio;Rua das Palmeiras;12;aberta;",
    "OC-011;acessibilidade;Calçada irregular dificulta cadeirante;Escola Municipal;14;concluida;20",
    "OC-012;conservacao;Playground com peças soltas;Parque do Bairro;15;em_analise;",
    "OC-013;iluminacao;Poste inclinado após chuva forte;Avenida Principal;16;aberta;",
    "OC-014;limpeza;Lixeira pública danificada;Praça Central;18;concluida;23",
    "OC-015;;Buraco na via sem categoria informada;Rua das Oliveiras;19;aberta;",
    "OC-016;conservacao;Muro do parque pichado;Parque do Bairro;20;finalizada;"
]


# ============================================================
# SEÇÃO 3 - FUNÇÕES AUXILIARES DE EXIBIÇÃO
# ============================================================

def titulo(texto):
    """Imprime um título destacado para organizar a tela."""
    print()
    print("=" * 74)
    print(texto)
    print("=" * 74)


def subtitulo(texto):
    """Imprime um título menor."""
    print()
    print("-" * 74)
    print(texto)
    print("-" * 74)


# ============================================================
# SEÇÃO 4 - LEITURA DO ARQUIVO E VALIDAÇÃO
# ============================================================

def ler_linhas_do_arquivo():
    """
    Lê o arquivo dados/ocorrencias.csv e devolve a lista de linhas.
    O programa pode ser executado da pasta do projeto ou de dentro de src/,
    por isso tentamos mais de um caminho.
    Se não encontrar o arquivo, usa a cópia de reserva que está no código.
    """
    caminhos = ["dados/ocorrencias.csv",
                "../dados/ocorrencias.csv",
                "ocorrencias.csv"]

    for caminho in caminhos:
        try:
            arquivo = open(caminho, "r", encoding="utf-8")
            linhas = arquivo.readlines()
            arquivo.close()
            print("Dados carregados do arquivo:", caminho)
            return linhas
        except FileNotFoundError:
            pass   # tenta o próximo caminho

    print("AVISO: arquivo CSV não encontrado. Usando a cópia de reserva do código.")
    return LINHAS_RESERVA


def validar_registro(id_oc, categoria, descricao, local, dia_texto, situacao):
    """
    Verifica se um registro pode entrar no sistema.
    Devolve "" (texto vazio) quando está tudo certo,
    ou o motivo do problema quando há algo errado.
    """

    # Expressão booleana que resume a validação.
    # Ela usa AND, NOT e OR ao mesmo tempo:
    # o registro só é válido se TODAS as partes forem verdadeiras.
    registro_valido = ((id_oc != "")
                       and (categoria in CATEGORIAS)
                       and (situacao in SITUACOES)
                       and dia_texto.isdigit()
                       and not (local == "" or descricao == ""))

    if registro_valido:
        return ""

    # Se chegou até aqui o registro tem algum problema.
    # Os testes abaixo descobrem qual é, para dar uma mensagem específica.
    if id_oc == "":
        return "código ausente"
    elif categoria == "":
        return "categoria ausente"
    elif not (categoria in CATEGORIAS):
        return "categoria desconhecida (" + categoria + ")"
    elif situacao == "":
        return "situação ausente"
    elif not (situacao in SITUACOES):
        return "situação desconhecida (" + situacao + ")"
    elif not dia_texto.isdigit():
        return "dia de abertura inválido (" + dia_texto + ")"
    else:
        return "descrição ou local ausente"


def carregar_ocorrencias():
    """
    Transforma cada linha do arquivo em uma ocorrência (dicionário)
    e guarda na lista. Registros com problema são separados.
    """
    global total_linhas_lidas

    linhas = ler_linhas_do_arquivo()

    # Começa em 1 porque a linha 0 é o cabeçalho do arquivo.
    for i in range(1, len(linhas)):
        linha = linhas[i].strip()

        if linha == "":
            continue   # pula linhas em branco

        total_linhas_lidas = total_linhas_lidas + 1
        campos = linha.split(";")

        # Se a linha tiver menos campos que o esperado, completa com vazio
        # para o programa não quebrar ao acessar uma posição que não existe.
        while len(campos) < 7:
            campos.append("")

        id_oc = campos[0].strip()
        categoria = campos[1].strip()
        descricao = campos[2].strip()
        local = campos[3].strip()
        dia_texto = campos[4].strip()
        situacao = campos[5].strip()
        dia_conclusao_texto = campos[6].strip()

        problema = validar_registro(id_oc, categoria, descricao,
                                    local, dia_texto, situacao)

        if problema != "":
            registros_rejeitados.append({"id": id_oc, "motivo": problema})
            continue   # não entra no sistema

        # Converte os dias de texto para número.
        # O dia de conclusão vale 0 quando a ocorrência ainda não foi concluída.
        dia_abertura = int(dia_texto)
        if dia_conclusao_texto.isdigit():
            dia_conclusao = int(dia_conclusao_texto)
        else:
            dia_conclusao = 0

        ocorrencia = {
            "id": id_oc,
            "categoria": categoria,
            "descricao": descricao,
            "local": local,
            "dia_abertura": dia_abertura,
            "status": situacao,
            "dia_conclusao": dia_conclusao
        }

        ocorrencias.append(ocorrencia)        # entra na LISTA
        indice_por_id[id_oc] = ocorrencia     # entra no DICIONÁRIO

        # Se está aberta, entra no fim da FILA de análise.
        if situacao == "aberta":
            fila_analise.append(id_oc)


def carregar_historico_inicial():
    """
    Empilha os eventos de acompanhamento que já aconteceram no bairro.
    São 12 atualizações simuladas (o enunciado pede no mínimo 8).
    Cada evento entra no topo da PILHA, então o mais recente fica por último.
    """
    eventos = [
        ("OC-001", "aberta", "em_analise", 4),
        ("OC-003", "aberta", "em_analise", 5),
        ("OC-005", "aberta", "em_analise", 8),
        ("OC-001", "em_analise", "concluida", 9),
        ("OC-006", "aberta", "em_analise", 9),
        ("OC-006", "em_analise", "concluida", 12),
        ("OC-009", "aberta", "em_analise", 13),
        ("OC-011", "aberta", "em_analise", 16),
        ("OC-012", "aberta", "em_analise", 17),
        ("OC-011", "em_analise", "concluida", 20),
        ("OC-014", "aberta", "em_analise", 20),
        ("OC-014", "em_analise", "concluida", 23)
    ]

    for evento in eventos:
        registrar_no_historico(evento[0], evento[1], evento[2], evento[3])


# ============================================================
# SEÇÃO 5 - PILHA DE HISTÓRICO
# ============================================================

def registrar_no_historico(id_oc, situacao_antiga, situacao_nova, dia):
    """Coloca uma atualização no topo da PILHA de histórico."""
    evento = {
        "id": id_oc,
        "de": situacao_antiga,
        "para": situacao_nova,
        "dia": dia
    }
    pilha_historico.append(evento)   # append = empilhar


def mostrar_historico(quantidade):
    """
    Mostra as últimas atualizações, da mais recente para a mais antiga.
    Percorremos a pilha de trás para frente porque o topo é o fim da lista.
    """
    subtitulo("HISTÓRICO DE ATUALIZAÇÕES (mais recentes primeiro)")

    if len(pilha_historico) == 0:
        print("Nenhuma atualização registrada.")
        return

    mostrados = 0
    posicao = len(pilha_historico) - 1   # topo da pilha

    while posicao >= 0 and mostrados < quantidade:
        evento = pilha_historico[posicao]
        print("dia " + str(evento["dia"]).rjust(2) + " | " +
              evento["id"] + " | " +
              NOME_SITUACAO[evento["de"]] + " -> " +
              NOME_SITUACAO[evento["para"]])
        posicao = posicao - 1
        mostrados = mostrados + 1

    print()
    print("Total de eventos no histórico:", len(pilha_historico))


# ============================================================
# SEÇÃO 6 - LISTAGEM E CONSULTAS
# ============================================================

def mostrar_cabecalho_tabela():
    print("CÓDIGO   | CATEGORIA      | LOCAL                  | SITUAÇÃO")
    print("-" * 74)


def mostrar_linha(ocorrencia):
    """Mostra uma ocorrência em formato de tabela."""
    print(ocorrencia["id"].ljust(8) + " | " +
          NOME_CATEGORIA[ocorrencia["categoria"]].ljust(14) + " | " +
          ocorrencia["local"].ljust(22) + " | " +
          NOME_SITUACAO[ocorrencia["status"]])


def listar_ocorrencias(lista):
    """Mostra uma lista de ocorrências em forma de tabela."""
    if len(lista) == 0:
        print("Nenhuma ocorrência encontrada com esse critério.")
        return

    mostrar_cabecalho_tabela()
    for ocorrencia in lista:
        mostrar_linha(ocorrencia)
    print("-" * 74)
    print("Total exibido:", len(lista), "ocorrência(s)")


def buscar_por_id(id_procurado):
    """
    Procura uma ocorrência pelo código usando o DICIONÁRIO.
    O dicionário encontra o registro direto, sem percorrer a lista toda.
    Devolve a ocorrência ou None se não existir.
    """
    id_procurado = id_procurado.strip().upper()

    if id_procurado in indice_por_id:
        return indice_por_id[id_procurado]
    else:
        return None


def mostrar_ocorrencia_completa(ocorrencia):
    """Mostra todos os dados de uma ocorrência."""
    print("Código...........:", ocorrencia["id"])
    print("Categoria........:", NOME_CATEGORIA[ocorrencia["categoria"]])
    print("Descrição........:", ocorrencia["descricao"])
    print("Local............:", ocorrencia["local"])
    print("Aberta no dia....:", ocorrencia["dia_abertura"])
    print("Situação.........:", NOME_SITUACAO[ocorrencia["status"]])
    print("  (significado)  :", SIGNIFICADO_SITUACAO[ocorrencia["status"]])

    if ocorrencia["dia_conclusao"] > 0:
        dias = ocorrencia["dia_conclusao"] - ocorrencia["dia_abertura"]
        print("Concluída no dia.:", ocorrencia["dia_conclusao"],
              "(levou", dias, "dias)")
    else:
        dias_em_aberto = DIA_ATUAL - ocorrencia["dia_abertura"]
        print("Em acompanhamento há:", dias_em_aberto, "dias")


def filtrar_por_categoria(categoria):
    """Devolve a lista de ocorrências de uma categoria."""
    encontradas = []
    for ocorrencia in ocorrencias:
        if ocorrencia["categoria"] == categoria:
            encontradas.append(ocorrencia)
    return encontradas


def filtrar_por_situacao(situacao):
    """Devolve a lista de ocorrências em uma situação."""
    encontradas = []
    for ocorrencia in ocorrencias:
        if ocorrencia["status"] == situacao:
            encontradas.append(ocorrencia)
    return encontradas


def filtrar_por_categoria_e_situacao(categoria, situacao):
    """
    Filtro combinado: usa o operador AND para exigir as duas condições.
    Só entra na lista a ocorrência que for da categoria E da situação pedidas.
    """
    encontradas = []
    for ocorrencia in ocorrencias:
        if ocorrencia["categoria"] == categoria and ocorrencia["status"] == situacao:
            encontradas.append(ocorrencia)
    return encontradas


def listar_pendentes():
    """
    Pendentes são as ocorrências que ainda não foram concluídas,
    ou seja, as que estão abertas OU em análise.
    Usamos o operador NOT para dizer "tudo que não está concluído".
    """
    encontradas = []
    for ocorrencia in ocorrencias:
        if not (ocorrencia["status"] == "concluida"):
            encontradas.append(ocorrencia)
    return encontradas


# ============================================================
# SEÇÃO 7 - CADASTRO DE NOVAS OCORRÊNCIAS
# ============================================================

def gerar_novo_id():
    """Cria um código único para uma nova ocorrência."""
    numero = total_linhas_lidas + 1
    while True:
        novo_id = "OC-" + str(numero).zfill(3)
        if not (novo_id in indice_por_id):
            return novo_id
        numero = numero + 1


def cadastrar_ocorrencia(categoria, descricao, local, dia_abertura):
    """
    Cadastra uma nova ocorrência depois de validar os campos obrigatórios.
    Devolve o código criado, ou "" se o cadastro foi recusado.
    """
    categoria = categoria.strip().lower()
    descricao = descricao.strip()
    local = local.strip()
    dia_texto = str(dia_abertura).strip()

    novo_id = gerar_novo_id()

    # Toda ocorrência nova entra como "aberta".
    problema = validar_registro(novo_id, categoria, descricao,
                                local, dia_texto, "aberta")

    if problema != "":
        print("CADASTRO RECUSADO:", problema)
        print("Campos obrigatórios:", ", ".join(CAMPOS_OBRIGATORIOS))
        print("Categorias aceitas :", ", ".join(CATEGORIAS))
        return ""

    ocorrencia = {
        "id": novo_id,
        "categoria": categoria,
        "descricao": descricao,
        "local": local,
        "dia_abertura": int(dia_texto),
        "status": "aberta",
        "dia_conclusao": 0
    }

    ocorrencias.append(ocorrencia)       # LISTA
    indice_por_id[novo_id] = ocorrencia  # DICIONÁRIO
    fila_analise.append(novo_id)         # entra no fim da FILA

    print("CADASTRO REALIZADO com o código", novo_id)
    return novo_id


# ============================================================
# SEÇÃO 8 - ATUALIZAÇÃO DE SITUAÇÃO
# ============================================================

def atualizar_situacao(id_oc, situacao_nova, dia):
    """
    Muda a situação de uma ocorrência e registra a mudança no histórico.
    Devolve True se conseguiu e False se recusou a mudança.
    """
    situacao_nova = situacao_nova.strip().lower()
    ocorrencia = buscar_por_id(id_oc)

    # Primeira condição: a ocorrência precisa existir.
    if ocorrencia == None:
        print("ERRO: não existe nenhuma ocorrência com o código", id_oc)
        return False

    # Segunda condição: a situação precisa ser uma das três conhecidas.
    if not (situacao_nova in SITUACOES):
        print("ERRO: situação desconhecida (" + situacao_nova + ")")
        print("Situações válidas:", ", ".join(SITUACOES))
        return False

    # Terceira condição: não faz sentido mudar para a mesma situação.
    if ocorrencia["status"] == situacao_nova:
        print("AVISO: a ocorrência", ocorrencia["id"],
              "já está na situação", NOME_SITUACAO[situacao_nova])
        return False

    situacao_antiga = ocorrencia["status"]
    ocorrencia["status"] = situacao_nova

    # Quando conclui, guarda o dia para o cálculo do tempo de atendimento.
    if situacao_nova == "concluida":
        ocorrencia["dia_conclusao"] = dia
    else:
        ocorrencia["dia_conclusao"] = 0

    # Mantém a FILA coerente: ela só contém ocorrências abertas.
    if situacao_nova == "aberta":
        if not (ocorrencia["id"] in fila_analise):
            fila_analise.append(ocorrencia["id"])
    else:
        if ocorrencia["id"] in fila_analise:
            fila_analise.remove(ocorrencia["id"])

    registrar_no_historico(ocorrencia["id"], situacao_antiga,
                           situacao_nova, dia)

    print("ATUALIZADO:", ocorrencia["id"], "passou de",
          NOME_SITUACAO[situacao_antiga], "para",
          NOME_SITUACAO[situacao_nova], "no dia", dia)
    return True


# ============================================================
# SEÇÃO 9 - FILA DE ANÁLISE
# ============================================================

def mostrar_fila():
    """Mostra a fila de ocorrências esperando análise, por ordem de chegada."""
    subtitulo("FILA DE ANÁLISE (ordem de chegada - o primeiro a entrar sai primeiro)")

    if len(fila_analise) == 0:
        print("A fila está vazia: nenhuma ocorrência aguardando análise.")
        return

    posicao = 1
    for id_oc in fila_analise:
        ocorrencia = indice_por_id[id_oc]
        print(str(posicao) + "º | " + id_oc + " | " +
              NOME_CATEGORIA[ocorrencia["categoria"]].ljust(14) + " | " +
              "aberta no dia " + str(ocorrencia["dia_abertura"]))
        posicao = posicao + 1

    print()
    print("Total na fila:", len(fila_analise))
    print("Próxima a ser analisada:", fila_analise[0])


def atender_proxima_da_fila(dia):
    """
    Atende a ocorrência mais antiga da fila, passando ela para análise.
    É aqui que a fila funciona como fila: sai quem entrou primeiro.
    """
    if len(fila_analise) == 0:
        print("Não há ocorrências aguardando análise.")
        return

    id_oc = fila_analise[0]   # primeiro da fila
    print("Retirando da fila a ocorrência mais antiga:", id_oc)
    atualizar_situacao(id_oc, "em_analise", dia)


# ============================================================
# SEÇÃO 10 - HIERARQUIA BAIRRO > CATEGORIA > OCORRÊNCIAS
# ============================================================

def montar_hierarquia():
    """
    Monta um dicionário dentro de outro dicionário para organizar
    as ocorrências por bairro e, dentro dele, por categoria.
    """
    hierarquia = {}
    hierarquia[BAIRRO] = {}

    for categoria in CATEGORIAS:
        hierarquia[BAIRRO][categoria] = []

    for ocorrencia in ocorrencias:
        categoria = ocorrencia["categoria"]
        hierarquia[BAIRRO][categoria].append(ocorrencia["id"])

    return hierarquia


def mostrar_hierarquia():
    """Mostra a hierarquia em forma de árvore."""
    subtitulo("ORGANIZAÇÃO HIERÁRQUICA: BAIRRO > CATEGORIA > OCORRÊNCIAS")

    hierarquia = montar_hierarquia()

    for bairro in hierarquia:
        print(bairro)
        for categoria in hierarquia[bairro]:
            lista_ids = hierarquia[bairro][categoria]
            print("   |- " + NOME_CATEGORIA[categoria] +
                  " (" + str(len(lista_ids)) + " ocorrências)")
            for id_oc in lista_ids:
                ocorrencia = indice_por_id[id_oc]
                print("   |     " + id_oc + " - " +
                      ocorrencia["local"] + " - " +
                      NOME_SITUACAO[ocorrencia["status"]])


# ============================================================
# SEÇÃO 11 - INDICADORES
# ============================================================

def calcular_percentual(parte, total):
    """Calcula quanto a parte representa do total, em porcentagem."""
    if total == 0:
        return 0.0
    return round((parte / total) * 100, 1)


def contar_por_categoria():
    """Conta quantas ocorrências existem em cada categoria."""
    contagem = {}
    for categoria in CATEGORIAS:
        contagem[categoria] = 0

    for ocorrencia in ocorrencias:
        categoria = ocorrencia["categoria"]
        contagem[categoria] = contagem[categoria] + 1

    return contagem


def contar_por_situacao():
    """Conta quantas ocorrências existem em cada situação."""
    contagem = {}
    for situacao in SITUACOES:
        contagem[situacao] = 0

    for ocorrencia in ocorrencias:
        situacao = ocorrencia["status"]
        contagem[situacao] = contagem[situacao] + 1

    return contagem


def montar_matriz_categoria_situacao():
    """
    Monta uma MATRIZ (lista de listas) com a quantidade de ocorrências.
    Cada linha é uma categoria e cada coluna é uma situação.
    """
    matriz = []

    for categoria in CATEGORIAS:
        linha = []
        for situacao in SITUACOES:
            total = 0
            for ocorrencia in ocorrencias:
                if ocorrencia["categoria"] == categoria and ocorrencia["status"] == situacao:
                    total = total + 1
            linha.append(total)
        matriz.append(linha)

    return matriz


def calcular_tempo_medio_conclusao():
    """
    Indicador adicional: quantos dias, em média, uma ocorrência leva
    entre ser aberta e ser concluída.
    Fórmula: soma dos dias de cada ocorrência concluída / número de concluídas
    """
    soma_dias = 0
    quantidade = 0

    for ocorrencia in ocorrencias:
        if ocorrencia["status"] == "concluida" and ocorrencia["dia_conclusao"] > 0:
            dias = ocorrencia["dia_conclusao"] - ocorrencia["dia_abertura"]
            soma_dias = soma_dias + dias
            quantidade = quantidade + 1

    if quantidade == 0:
        return 0.0

    return round(soma_dias / quantidade, 1)


def mostrar_painel_indicadores():
    """Mostra o painel completo com os indicadores da comunidade."""
    titulo("PAINEL DE INDICADORES - " + BAIRRO + " (dia simulado " +
           str(DIA_ATUAL) + ")")

    total = len(ocorrencias)

    # ---- Origem dos dados ----
    print("ORIGEM DOS DADOS")
    print("  Linhas de dados lidas......:", total_linhas_lidas)
    print("  Registros válidos..........:", total)
    print("  Registros recusados........:", len(registros_rejeitados))

    for registro in registros_rejeitados:
        print("     - " + registro["id"] + ": " + registro["motivo"])

    # ---- Por categoria ----
    subtitulo("OCORRÊNCIAS POR CATEGORIA")
    print("Regra de cálculo: percentual = (total da categoria / total geral) x 100")
    print()
    print("CATEGORIA        | TOTAL | PERCENTUAL")
    print("-" * 74)

    contagem_categoria = contar_por_categoria()
    for categoria in CATEGORIAS:
        quantidade = contagem_categoria[categoria]
        percentual = calcular_percentual(quantidade, total)
        print(NOME_CATEGORIA[categoria].ljust(16) + " | " +
              str(quantidade).rjust(5) + " | " +
              str(percentual) + "%")

    print("-" * 74)
    print("TOTAL".ljust(16) + " | " + str(total).rjust(5) + " | 100.0%")

    # ---- Por situação ----
    subtitulo("OCORRÊNCIAS POR SITUAÇÃO")
    print("SITUAÇÃO         | TOTAL | PERCENTUAL | SIGNIFICADO")
    print("-" * 74)

    contagem_situacao = contar_por_situacao()
    for situacao in SITUACOES:
        quantidade = contagem_situacao[situacao]
        percentual = calcular_percentual(quantidade, total)
        print(NOME_SITUACAO[situacao].ljust(16) + " | " +
              str(quantidade).rjust(5) + " | " +
              (str(percentual) + "%").rjust(10) + " | " +
              SIGNIFICADO_SITUACAO[situacao])

    # ---- Matriz ----
    subtitulo("MATRIZ CATEGORIA x SITUAÇÃO (quantidade de ocorrências)")
    print("CATEGORIA        | Aberta | Análise | Concluída | TOTAL")
    print("-" * 74)

    matriz = montar_matriz_categoria_situacao()

    for i in range(len(CATEGORIAS)):
        linha = matriz[i]
        total_linha = 0
        for valor in linha:
            total_linha = total_linha + valor

        print(NOME_CATEGORIA[CATEGORIAS[i]].ljust(16) + " | " +
              str(linha[0]).rjust(6) + " | " +
              str(linha[1]).rjust(7) + " | " +
              str(linha[2]).rjust(9) + " | " +
              str(total_linha).rjust(5))

    print("-" * 74)

    # soma de cada coluna da matriz
    print("TOTAL".ljust(16) + " | " +
          str(contagem_situacao["aberta"]).rjust(6) + " | " +
          str(contagem_situacao["em_analise"]).rjust(7) + " | " +
          str(contagem_situacao["concluida"]).rjust(9) + " | " +
          str(total).rjust(5))

    # ---- Indicadores adicionais ----
    subtitulo("INDICADORES ADICIONAIS")

    tempo_medio = calcular_tempo_medio_conclusao()
    pendentes = listar_pendentes()

    print("Tempo médio de conclusão")
    print("  Fórmula: soma dos dias entre abertura e conclusão / nº de concluídas")
    print("  Dados de origem:")

    for ocorrencia in ocorrencias:
        if ocorrencia["status"] == "concluida" and ocorrencia["dia_conclusao"] > 0:
            dias = ocorrencia["dia_conclusao"] - ocorrencia["dia_abertura"]
            print("     " + ocorrencia["id"] + ": dia " +
                  str(ocorrencia["dia_abertura"]) + " ate dia " +
                  str(ocorrencia["dia_conclusao"]) + " = " + str(dias) + " dias")

    print("  Resultado:", tempo_medio, "dias")
    print()
    print("Demandas pendentes (abertas ou em análise):", len(pendentes),
          "de", total, "(" + str(calcular_percentual(len(pendentes), total)) + "%)")
    print("Aguardando a primeira análise (fila):", len(fila_analise))
    print("Eventos registrados no histórico:", len(pilha_historico))

    # ---- Conclusão automática ----
    subtitulo("LEITURA DOS NÚMEROS")

    # Descobre a categoria com mais ocorrências percorrendo a contagem.
    categoria_lider = CATEGORIAS[0]
    for categoria in CATEGORIAS:
        if contagem_categoria[categoria] > contagem_categoria[categoria_lider]:
            categoria_lider = categoria

    print("- A categoria com mais registros é " +
          NOME_CATEGORIA[categoria_lider] + ", com " +
          str(contagem_categoria[categoria_lider]) + " ocorrências (" +
          str(calcular_percentual(contagem_categoria[categoria_lider], total)) +
          "% do total).")
    print("- " + str(len(pendentes)) + " das " + str(total) +
          " demandas ainda não foram concluídas, o que mostra que a maior parte")
    print("  do esforço da comunidade ainda está concentrada em acompanhamento.")
    print("- As demandas concluídas levaram em média " + str(tempo_medio) +
          " dias entre o registro e o encerramento.")


# ============================================================
# SEÇÃO 12 - MODO DEMONSTRAÇÃO
# ============================================================

def demonstracao():
    """
    Executa automaticamente um roteiro completo de uso do sistema.
    Serve para apresentar o projeto sem precisar digitar no menu.
    """
    titulo("DEMONSTRAÇÃO AUTOMÁTICA DO SISTEMA")

    # --- 1. Listagem ---
    subtitulo("1. LISTAGEM DE TODAS AS OCORRÊNCIAS VÁLIDAS")
    listar_ocorrencias(ocorrencias)

    print()
    print("Registros recusados pela validação:")
    for registro in registros_rejeitados:
        print("   " + registro["id"] + " -> " + registro["motivo"])

    # --- 2. Busca por código ---
    subtitulo("2. BUSCA POR CÓDIGO")
    print(">> Procurando a ocorrência OC-003:")
    encontrada = buscar_por_id("OC-003")
    if encontrada != None:
        mostrar_ocorrencia_completa(encontrada)

    print()
    print(">> Procurando um código que não existe (OC-999):")
    nao_existe = buscar_por_id("OC-999")
    if nao_existe == None:
        print("Nenhuma ocorrência encontrada com o código OC-999.")

    # --- 3. Filtros ---
    subtitulo("3. FILTROS")
    print(">> Todas as ocorrências de Iluminação:")
    listar_ocorrencias(filtrar_por_categoria("iluminacao"))

    print()
    print(">> Todas as ocorrências Abertas:")
    listar_ocorrencias(filtrar_por_situacao("aberta"))

    print()
    print(">> Filtro combinado (categoria Limpeza E situação Aberta):")
    listar_ocorrencias(filtrar_por_categoria_e_situacao("limpeza", "aberta"))

    # --- 4. Cadastro ---
    subtitulo("4. CADASTRO DE NOVAS OCORRÊNCIAS")
    print(">> Cadastro válido:")
    cadastrar_ocorrencia("iluminacao", "Poste sem lâmpada na entrada do parque",
                         "Parque do Bairro", 24)

    print()
    print(">> Cadastro inválido (categoria em branco):")
    cadastrar_ocorrencia("", "Problema sem categoria informada",
                         "Rua das Palmeiras", 24)

    print()
    print(">> Cadastro inválido (categoria que não existe):")
    cadastrar_ocorrencia("transito", "Semáforo com defeito",
                         "Avenida Principal", 24)

    # --- 5. Atualização de situação ---
    subtitulo("5. ATUALIZAÇÃO DE SITUAÇÃO")
    print(">> Atualização válida (OC-002 passa para em análise):")
    atualizar_situacao("OC-002", "em_analise", DIA_ATUAL)

    print()
    print(">> Atualização válida (OC-003 passa para concluída):")
    atualizar_situacao("OC-003", "concluida", DIA_ATUAL)

    print()
    print(">> Atualização inválida (situação desconhecida):")
    atualizar_situacao("OC-004", "finalizada", DIA_ATUAL)

    print()
    print(">> Atualização inválida (código inexistente):")
    atualizar_situacao("OC-999", "concluida", DIA_ATUAL)

    # --- 6. Fila ---
    subtitulo("6. FILA DE ANÁLISE")
    mostrar_fila()
    print()
    print(">> Atendendo a próxima da fila:")
    atender_proxima_da_fila(DIA_ATUAL)
    print()
    mostrar_fila()

    # --- 7. Pilha de histórico ---
    mostrar_historico(10)

    # --- 8. Hierarquia ---
    mostrar_hierarquia()

    # --- 9. Indicadores ---
    mostrar_painel_indicadores()

    titulo("FIM DA DEMONSTRAÇÃO")


# ============================================================
# SEÇÃO 13 - MENU (INTERFACE TEXTUAL)
# ============================================================

def mostrar_menu():
    print()
    print("=" * 74)
    print("NEIGHBORHOOD ACTION DASHBOARD - " + BAIRRO)
    print("=" * 74)
    print(" 1 - Listar todas as ocorrências")
    print(" 2 - Buscar ocorrência por código")
    print(" 3 - Filtrar por categoria")
    print(" 4 - Filtrar por situação")
    print(" 5 - Cadastrar nova ocorrência")
    print(" 6 - Atualizar situação de uma ocorrência")
    print(" 7 - Ver fila de análise")
    print(" 8 - Ver histórico de atualizações")
    print(" 9 - Ver organização hierárquica do bairro")
    print("10 - Painel de indicadores")
    print("11 - Rodar demonstração automática")
    print(" 0 - Sair")
    print("-" * 74)


def menu_buscar():
    codigo = input("Digite o código da ocorrência (exemplo: OC-003): ")
    ocorrencia = buscar_por_id(codigo)

    if ocorrencia == None:
        print("Nenhuma ocorrência encontrada com o código", codigo.strip().upper())
    else:
        print()
        mostrar_ocorrencia_completa(ocorrencia)


def menu_filtrar_categoria():
    print("Categorias disponíveis:", ", ".join(CATEGORIAS))
    categoria = input("Digite a categoria: ").strip().lower()

    if not (categoria in CATEGORIAS):
        print("ERRO: categoria desconhecida. Use uma das categorias da lista.")
        return

    listar_ocorrencias(filtrar_por_categoria(categoria))


def menu_filtrar_situacao():
    print("Situações disponíveis:", ", ".join(SITUACOES))
    situacao = input("Digite a situação: ").strip().lower()

    if not (situacao in SITUACOES):
        print("ERRO: situação desconhecida. Use uma das situações da lista.")
        return

    listar_ocorrencias(filtrar_por_situacao(situacao))


def menu_cadastrar():
    print("Categorias disponíveis:", ", ".join(CATEGORIAS))
    categoria = input("Categoria.....: ")
    descricao = input("Descrição.....: ")
    local = input("Local.........: ")
    dia = input("Dia da abertura (1 a 30): ")

    cadastrar_ocorrencia(categoria, descricao, local, dia)


def menu_atualizar():
    codigo = input("Código da ocorrência: ")
    print("Situações disponíveis:", ", ".join(SITUACOES))
    situacao = input("Nova situação.......: ")

    atualizar_situacao(codigo, situacao, DIA_ATUAL)


def executar_menu():
    """Laço principal do programa."""
    continuar = True

    while continuar:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_ocorrencias(ocorrencias)
        elif opcao == "2":
            menu_buscar()
        elif opcao == "3":
            menu_filtrar_categoria()
        elif opcao == "4":
            menu_filtrar_situacao()
        elif opcao == "5":
            menu_cadastrar()
        elif opcao == "6":
            menu_atualizar()
        elif opcao == "7":
            mostrar_fila()
        elif opcao == "8":
            mostrar_historico(10)
        elif opcao == "9":
            mostrar_hierarquia()
        elif opcao == "10":
            mostrar_painel_indicadores()
        elif opcao == "11":
            demonstracao()
        elif opcao == "0":
            print()
            print("Encerrando o painel comunitário. Até logo!")
            continuar = False
        else:
            print("Opção inválida. Digite um número de 0 a 11.")


# ============================================================
# SEÇÃO 14 - INÍCIO DO PROGRAMA
# ============================================================

titulo("NEIGHBORHOOD ACTION DASHBOARD")
print("Painel comunitário de ocorrências do bairro", BAIRRO)
print("Global Solution 2026.2 - FIAP - case CitizenTech")
print()

carregar_ocorrencias()
carregar_historico_inicial()

print("Ocorrências válidas carregadas:", len(ocorrencias))
print("Registros recusados pela validação:", len(registros_rejeitados))
print("Eventos no histórico:", len(pilha_historico))

executar_menu()
