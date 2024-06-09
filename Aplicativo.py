import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Você não pode sacar o que não tem. PARA DE SER DOIDA! @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Toma! Vê se não gasta tudo de uma vez ===")
            return True

        else:
            print("\n@@@ OI? Valor inválido Q-U-E-R-I-D-I-N-H-A! @@@")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Só isso? Bom, vou guardar sua mixaria ===")
        else:
            print("\n@@@ OI? Valor inválido Q-U-E-R-I-D-I-N-H-A! @@@")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Aqui tem regras benhê, saque acima do seu limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Já tá bom! Esgotou a quantidade diária de saques. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
,
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Depósito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """\n

            ESTE É O APLICATIVO DO SEMCRED
      
     Digite a opção desejada, seja breve e não me amole:

    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo usuário
    [5]\tNova conta
    [6]\tListar contas
    [0]\tVazar
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Oi, cadê sua conta? Ah não tem? Que PENA! Faça uma e depois volte aqui! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Qual seu CPF benzinho? ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não achei seu belo CPF aqui no meu cadastro. Faça o cadastro de cliente primeiro, seu afobado! @@@")
        return

    valor = float(input("Ah, finalmente resolveu guardar um dinheiro? Digite a mixaria que deseja depositar: "))
    transacao = Depósito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Qual seu CPF benzinho? ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não achei seu belo CPF aqui no meu cadastro. Faça o cadastro de cliente primeiro, seu afobado! @@@")
        return

    valor = float(input("Ah, já vai gastar a mixaria? Digite o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Qual seu CPF benzinho? ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não achei seu belo CPF aqui no meu cadastro. Faça o cadastro de cliente primeiro, seu afobado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO SEMCRED================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "NÃO TEM NADA AQUI!"
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Digite seu CPF, mas ATENÇÃO, somente números viu? ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já esqueceu de mim? Já tem um CPF igualzinho ao seu no meu sistema... @@@")
        return

    nome = input("Digite seu belo nome, mas quero ele completo, não me esconda nada: ")
    data_nascimento = input("Digite a data que o mundo foi agraciado com sua presença. Mas atenção o formato é dd-mm-aaaa: ")
    endereco = input("E onde você mora? Rua, Bairro, Cidade, Estado e CEP. Essa informação é importante para eu NUNCA passar perto: ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Pronto, agora você já é um de nossos amados clientes! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite seu CPF, benzinho: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não achei seu belo CPF aqui no meu cadastro. Faça o cadastro de cliente primeiro, seu afobado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print(f"\n=== Vê se anota para eu não ter que passar novamente! Agência: 0001 Conta: {numero_conta} ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            criar_cliente(clientes)

        elif opcao == "5":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "6":
            listar_contas(contas)

        elif opcao == "0":
            print("Já vai tarde!")
            break

        else:
            print("\n@@@ VOCÊ ESTÁ VENDO ESTE NÚMERO NO MENU? @@@")


main()